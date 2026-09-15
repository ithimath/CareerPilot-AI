"""Auth router — token verification and user registration helpers"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.core.dependencies import get_current_user
from app.core.firebase import get_firestore
from app.core.config import settings
from datetime import datetime
import httpx
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class AutoConfirmRequest(BaseModel):
    email: str


def init_user_profile_and_score(uid: str, email: str = "", name: str = "") -> dict:
    """
    Creates a Firestore profile document and a zero-initialized jobScores document
    if they do not yet exist. Idempotent.
    """
    db = get_firestore()
    now = datetime.utcnow()

    # ── Profile document ─────────────────────────────────────────────────
    profile_ref = db.collection("profiles").document(uid)
    profile_doc = profile_ref.get()

    if not profile_doc.exists:
        profile_data = {
            "uid": uid,
            "name": name,
            "email": email,
            "college": "",
            "degree": "",
            "department": "",
            "current_year": 0,
            "cgpa": 0.0,
            "skills": [],
            "interests": [],
            "projects": [],
            "internships": [],
            "certifications": [],
            "github_url": "",
            "linkedin_url": "",
            "portfolio_url": "",
            "profile_picture_url": "",
            "target_career": "",
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }
        profile_ref.set(profile_data)
        profile_created = True
    else:
        profile_created = False

    # ── jobScores document ───────────────────────────────────────────────
    score_ref = db.collection("jobScores").document(uid)
    score_doc = score_ref.get()

    if not score_doc.exists:
        zero_score = {
            "uid": uid,
            "total_score": 0.0,
            "skills_score": 0.0,
            "projects_score": 0.0,
            "interviews_score": 0.0,
            "resume_score": 0.0,
            "assessments_score": 0.0,
            "certificates_score": 0.0,
            "profile_score": 0.0,
            "internships_score": 0.0,
            "confidence_level": "Insufficient Data",
            "data_quality_notice": "New account — complete profile activities to build your score.",
            "prediction_method": "rule_based",
            "prediction_label": "Awaiting profile data",
            "positive_drivers": [],
            "suggestions": [
                "Add technical skills to your profile.",
                "Describe at least one project with a GitHub link.",
                "Complete an AI Mock Interview session.",
            ],
            "history": [],
            "updated_at": now.isoformat(),
        }
        score_ref.set(zero_score)
        score_created = True
    else:
        score_created = False

    return {
        "created": profile_created or score_created,
        "uid": uid,
        "profile_created": profile_created,
        "score_initialized": score_created,
        "message": "Profile and score initialized." if profile_created else "Profile already exists.",
    }


@router.post("/register")
async def register_user(payload: RegisterRequest):
    """
    Registers a new candidate user using Supabase Admin API with email_confirm=True.
    This bypasses Supabase free-tier email rate limits (3/hour) and prevents
    the 'Email not confirmed' blocker.
    """
    if not settings.SUPABASE_SERVICE_ROLE_KEY or not settings.SUPABASE_URL:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase configuration missing on server."
        )

    headers = {
        "apikey": settings.SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        # 1. Try to create user with email_confirm=True
        create_payload = {
            "email": payload.email,
            "password": payload.password,
            "email_confirm": True,
            "user_metadata": {
                "full_name": payload.name,
                "display_name": payload.name,
            },
        }

        res = await client.post(
            f"{settings.SUPABASE_URL}/auth/v1/admin/users",
            headers=headers,
            json=create_payload,
        )

        uid = None
        if res.status_code in (200, 201):
            uid = res.json().get("id")
        elif res.status_code in (400, 422) and (
            "already been registered" in res.text.lower()
            or "email_exists" in res.text.lower()
            or "already registered" in res.text.lower()
        ):
            # User already registered (e.g. earlier failed attempt or unconfirmed)
            # Find the user and confirm their email + update password
            try:
                users_res = await client.get(
                    f"{settings.SUPABASE_URL}/auth/v1/admin/users?per_page=1000",
                    headers=headers,
                )
                if users_res.status_code == 200:
                    user_list = users_res.json().get("users", [])
                    matched = [u for u in user_list if (u.get("email") or "").strip().lower() == payload.email.strip().lower()]
                    if matched:
                        uid = matched[0]["id"]
                        # Auto-confirm and update password
                        update_payload = {
                            "password": payload.password,
                            "email_confirm": True,
                            "user_metadata": {
                                "full_name": payload.name,
                                "display_name": payload.name,
                            },
                        }
                        await client.put(
                            f"{settings.SUPABASE_URL}/auth/v1/admin/users/{uid}",
                            headers=headers,
                            json=update_payload,
                        )
            except Exception as e:
                logger.warning(f"Error handling existing user in register: {e}")

            if not uid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="An account with this email already exists. Please log in directly.",
                )
        else:
            err_data = {}
            try:
                err_data = res.json()
            except Exception:
                pass
            err_msg = err_data.get("msg") or err_data.get("message") or res.text
            raise HTTPException(
                status_code=res.status_code,
                detail=f"Registration failed: {err_msg}",
            )

        # 2. Initialize Firestore profile & zero-score doc for the user
        try:
            init_user_profile_and_score(uid, email=payload.email, name=payload.name)
        except Exception as e:
            logger.warning(f"Profile initialization warning: {e}")

        return {
            "success": True,
            "uid": uid,
            "email": payload.email,
            "message": "User registered and verified successfully.",
        }


@router.post("/auto-confirm")
async def auto_confirm_user(payload: AutoConfirmRequest):
    """
    Auto-confirms an existing user's email via Supabase Admin API.
    Resolves 'Email not confirmed' errors without needing email delivery.
    """
    if not settings.SUPABASE_SERVICE_ROLE_KEY or not settings.SUPABASE_URL:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase configuration missing on server."
        )

    headers = {
        "apikey": settings.SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        users_res = await client.get(
            f"{settings.SUPABASE_URL}/auth/v1/admin/users?per_page=1000",
            headers=headers,
        )
        if users_res.status_code != 200:
            raise HTTPException(
                status_code=users_res.status_code,
                detail="Failed to query user records.",
            )

        users = users_res.json().get("users", [])
        matched = [u for u in users if (u.get("email") or "").strip().lower() == payload.email.strip().lower()]
        if not matched:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No account found with email {payload.email}",
            )

        user_id = matched[0]["id"]
        update_res = await client.put(
            f"{settings.SUPABASE_URL}/auth/v1/admin/users/{user_id}",
            headers=headers,
            json={"email_confirm": True},
        )
        if update_res.status_code != 200:
            raise HTTPException(
                status_code=update_res.status_code,
                detail="Failed to confirm user email.",
            )

        # Ensure Firestore profile doc and zero-score doc exist
        try:
            name = (matched[0].get("user_metadata") or {}).get("full_name") or ""
            init_user_profile_and_score(user_id, email=payload.email, name=name)
        except Exception as e:
            logger.warning(f"Profile initialization warning during auto-confirm: {e}")

        return {
            "success": True,
            "uid": user_id,
            "email": payload.email,
            "message": "Email has been confirmed successfully.",
        }


@router.post("/verify")
async def verify_token(user: dict = Depends(get_current_user)):
    """Verify a Firebase/Supabase token and return user info."""
    return {
        "uid": user["uid"],
        "email": user.get("email", ""),
        "name": user.get("name", ""),
        "verified": True,
    }


@router.post("/create-profile")
async def create_user_profile(user: dict = Depends(get_current_user)):
    """
    Called after signup — creates a Firestore profile document
    AND a zero-initialized jobScores document if they do not yet exist.
    """
    try:
        uid = user["uid"]
        email = user.get("email", "")
        name = user.get("name", "")
        return init_user_profile_and_score(uid, email=email, name=name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Profile creation failed: {e}")

