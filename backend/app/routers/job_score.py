"""Job Score router"""
from fastapi import APIRouter, Depends, HTTPException
from app.core.dependencies import get_current_user
from app.core.firebase import get_firestore
from app.services.scoring_service import calculate_job_readiness_score, calculate_profile_completion
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("")
async def get_job_score(user: dict = Depends(get_current_user)):
    """
    Get the current job readiness score from Firestore for the specific user UID.
    - If user has previously saved career readiness data, return it.
    - If user is brand new (no saved score), return and initialize a 0 readiness score.
    """
    try:
        db = get_firestore()
        uid = user["uid"]
        doc = db.collection("jobScores").document(uid).get()
        if doc.exists:
            return doc.to_dict()

        # Check if user has an existing profile with populated skills/projects/certs
        profile_doc = db.collection("profiles").document(uid).get()
        if profile_doc.exists:
            profile = profile_doc.to_dict()
            if profile.get("skills") or profile.get("projects") or profile.get("certifications"):
                return await recalculate_job_score(user)

        # Brand new user initial 0 score
        initial_score = {
            "uid": uid,
            "total_score": 0.0,
            "skills_score": 0.0,
            "projects_score": 0.0,
            "internships_score": 0.0,
            "certificates_score": 0.0,
            "profile_score": 0.0,
            "suggestions": [
                "Welcome to CareerPilot AI! Complete your candidate profile and add technical skills to calculate your ML Career Readiness Score."
            ],
            "updated_at": datetime.utcnow().isoformat(),
        }

        db.collection("jobScores").document(uid).set(initial_score)
        return initial_score
    except Exception as e:
        logger.error(f"Failed to fetch job score for uid={user.get('uid')}: {e}")
        return {
            "uid": user.get("uid", "user_new"),
            "total_score": 0.0,
            "skills_score": 0.0,
            "projects_score": 0.0,
            "internships_score": 0.0,
            "certificates_score": 0.0,
            "profile_score": 0.0,
            "suggestions": [
                "Welcome to CareerPilot AI! Complete your candidate profile and add technical skills to calculate your ML Career Readiness Score."
            ],
            "updated_at": datetime.utcnow().isoformat(),
        }


@router.post("/recalculate")
async def recalculate_job_score(user: dict = Depends(get_current_user)):
    """Force recalculation of job readiness score for current authenticated user."""
    try:
        db = get_firestore()
        uid = user["uid"]
        profile_doc = db.collection("profiles").document(uid).get()
        if not profile_doc.exists:
            profile = {"uid": uid}
        else:
            profile = profile_doc.to_dict()

        score = calculate_job_readiness_score(profile)
        score_data = {
            **score.model_dump(),
            "uid": uid,
            "updated_at": datetime.utcnow().isoformat(),
        }
        db.collection("jobScores").document(uid).set(score_data)
        return score_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Score recalculation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
