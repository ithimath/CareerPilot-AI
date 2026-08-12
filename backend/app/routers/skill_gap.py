"""Skill Gap router"""
from fastapi import APIRouter, Depends, HTTPException
from app.core.dependencies import get_current_user
from app.core.firebase import get_firestore
from app.services.career_service import get_skill_gap_for_career
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("")
async def get_skill_gap(user: dict = Depends(get_current_user)):
    """Get skill gap report for the user's target career."""
    try:
        db = get_firestore()
        uid = user["uid"]

        profile_doc = db.collection("profiles").document(uid).get()
        if not profile_doc.exists:
            raise HTTPException(status_code=404, detail="Profile not found")

        profile = profile_doc.to_dict()
        target_career = profile.get("target_career", "")
        if not target_career:
            return {"message": "No target career selected", "gap": None}

        skills = profile.get("skills", [])
        gap = get_skill_gap_for_career(skills, target_career)

        # Store report in Firestore
        gap["uid"] = uid
        gap["generated_at"] = datetime.utcnow()
        db.collection("skillGapReports").document(uid).set(gap)

        return gap

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Skill gap failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/career/{career_title}")
async def get_skill_gap_for_specific_career(
    career_title: str, user: dict = Depends(get_current_user)
):
    """Get skill gap for any career (not just target)."""
    try:
        db = get_firestore()
        uid = user["uid"]

        profile_doc = db.collection("profiles").document(uid).get()
        if not profile_doc.exists:
            raise HTTPException(status_code=404, detail="Profile not found")

        skills = profile_doc.to_dict().get("skills", [])
        gap = get_skill_gap_for_career(skills, career_title)
        return gap

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
