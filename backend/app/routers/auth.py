"""Auth router — token verification helper"""
from fastapi import APIRouter, Depends, HTTPException
from app.core.dependencies import get_current_user
from app.core.firebase import get_firestore
from datetime import datetime

router = APIRouter()

@router.post("/verify")
async def verify_token(user: dict = Depends(get_current_user)):
    """Verify a Firebase token and return user info."""
    return {
        "uid": user["uid"],
        "email": user.get("email", ""),
        "name": user.get("name", ""),
        "verified": True,
    }

@router.post("/create-profile")
async def create_user_profile(user: dict = Depends(get_current_user)):
    """
    Called after signup — creates a Firestore profile document if not exists.
    """
    try:
        db = get_firestore()
        uid = user["uid"]
        profile_ref = db.collection("profiles").document(uid)
        doc = profile_ref.get()

        if not doc.exists:
            profile_data = {
                "uid": uid,
                "name": user.get("name", ""),
                "email": user.get("email", ""),
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
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
            profile_ref.set(profile_data)
            return {"created": True, "uid": uid}

        return {"created": False, "uid": uid, "message": "Profile already exists"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Profile creation failed: {e}")
