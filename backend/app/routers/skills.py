"""Skills router"""
from fastapi import APIRouter, Depends, HTTPException
from app.core.dependencies import get_current_user
from app.core.firebase import get_firestore
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


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
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/add")
async def add_skill(skill_data: dict, user: dict = Depends(get_current_user)):
    """Add a skill to the user's profile."""
    skill = skill_data.get("skill", "").strip()
    if not skill:
        raise HTTPException(status_code=400, detail="Skill name is required")
    try:
        db = get_firestore()
        uid = user["uid"]
        profile_ref = db.collection("profiles").document(uid)
        doc = profile_ref.get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Profile not found")

        existing = doc.to_dict().get("skills", [])
        skill_lower = skill.lower()
        if any(s.lower() == skill_lower for s in existing):
            return {"success": True, "message": "Skill already exists", "skills": existing}

        existing.append(skill)
        profile_ref.update({"skills": existing, "updated_at": datetime.utcnow()})
        return {"success": True, "skills": existing}
    except HTTPException:
        raise
    except Exception as e:
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
        updated = [s for s in existing if s.lower() != skill_name.lower()]
        profile_ref.update({"skills": updated, "updated_at": datetime.utcnow()})
        return {"success": True, "skills": updated}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
