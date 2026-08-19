"""Skills router"""
from fastapi import APIRouter, Depends, HTTPException
from app.core.dependencies import get_current_user
from app.core.firebase import get_firestore
from app.schemas.models import SkillAddRequest
from app.services.scoring_service import calculate_job_readiness_score
from datetime import datetime
import html
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


def _skill_name(s) -> str:
    if isinstance(s, dict):
        return s.get("name", "")
    return str(s)


@router.get("")
async def get_skills(user: dict = Depends(get_current_user)):
    """Get all skills for the current user."""
    try:
        db = get_firestore()
        doc = db.collection("profiles").document(user["uid"]).get()
        if not doc.exists:
            return {"skills": []}
        return {"skills": doc.to_dict().get("skills", [])}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch skills.")


@router.post("/add")
async def add_skill(skill_data: SkillAddRequest, user: dict = Depends(get_current_user)):
    """Add a skill (with optional proficiency level) to the user's profile."""
    raw_name = skill_data.skill or skill_data.name or ""
    if not raw_name or not raw_name.strip():
        raise HTTPException(status_code=400, detail="Skill name is required")

    skill_name = html.escape(raw_name.strip()[:80])
    level = html.escape(skill_data.level.strip()[:30]) or "Intermediate"
    verified = bool(skill_data.verified)
    source = html.escape(skill_data.source.strip()[:30]) or "manual"

    try:
        db = get_firestore()
        uid = user["uid"]
        profile_ref = db.collection("profiles").document(uid)
        doc = profile_ref.get()
        if not doc.exists:
            profile_data = {"uid": uid, "skills": []}
            profile_ref.set(profile_data)
            existing = []
        else:
            profile_data = doc.to_dict()
            existing = profile_data.get("skills", [])

        # Check existing
        skill_lower = skill_name.lower()
        exists_idx = -1
        for idx, s in enumerate(existing):
            if _skill_name(s).lower() == skill_lower:
                exists_idx = idx
                break

        new_skill_entry = {
            "name": skill_name,
            "level": level,
            "verified": verified,
            "source": skill_data.get("source", "manual")
        }

        if exists_idx >= 0:
            existing[exists_idx] = new_skill_entry
        else:
            existing.append(new_skill_entry)

        profile_ref.update({"skills": existing, "updated_at": datetime.utcnow().isoformat()})

        # Recalculate score
        updated_profile = profile_ref.get().to_dict()
        readiness = calculate_job_readiness_score(updated_profile, action_reason=f"Added skill: {skill_name}")
        db.collection("jobScores").document(uid).set({
            **readiness.model_dump(),
            "uid": uid,
            "updated_at": datetime.utcnow().isoformat(),
        })

        return {
            "success": True,
            "skills": existing,
            "readiness_score": readiness.total_score,
            "message": f"Skill '{skill_name}' saved."
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add skill: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{skill_name}")
async def remove_skill(skill_name: str, user: dict = Depends(get_current_user)):
    """Remove a skill from the user's profile."""
    try:
        db = get_firestore()
        uid = user["uid"]
        profile_ref = db.collection("profiles").document(uid)
        doc = profile_ref.get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Profile not found")

        existing = doc.to_dict().get("skills", [])
        updated = [s for s in existing if _skill_name(s).lower() != skill_name.lower()]
        profile_ref.update({"skills": updated, "updated_at": datetime.utcnow().isoformat()})

        # Recalculate score
        updated_profile = profile_ref.get().to_dict()
        readiness = calculate_job_readiness_score(updated_profile, action_reason=f"Removed skill: {skill_name}")
        db.collection("jobScores").document(uid).set({
            **readiness.model_dump(),
            "uid": uid,
            "updated_at": datetime.utcnow().isoformat(),
        })

        return {
            "success": True,
            "skills": updated,
            "readiness_score": readiness.total_score,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

