"""Job Score router — Multi-Signal Career Readiness Engine"""
from fastapi import APIRouter, Depends, HTTPException
from app.core.dependencies import get_current_user
from app.core.firebase import get_firestore
from app.services.scoring_service import calculate_job_readiness_score, load_user_activities
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("")
async def get_job_score(user: dict = Depends(get_current_user)):
    """
    Get current live career readiness score for authenticated UID.
    Dynamically computes the score across candidate profile, projects,
    interviews, resume scans, assessments, and verified certificates.
    """
    return await recalculate_job_score(user)


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
            profile["uid"] = uid

        activities = load_user_activities(uid)
        score = calculate_job_readiness_score(profile, activities=activities, action_reason="User recalculation")
        
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
        logger.error(f"Score recalculation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_score_history(user: dict = Depends(get_current_user)):
    """Fetch score progression history entries for user UID."""
    try:
        db = get_firestore()
        uid = user["uid"]
        doc = db.collection("readinessHistory").document(uid).get()
        if doc.exists:
            return {"uid": uid, "history": doc.to_dict().get("history", [])}
        return {"uid": uid, "history": []}
    except Exception as e:
        logger.error(f"Failed to fetch score history for uid={user.get('uid')}: {e}")
        return {"uid": user.get("uid"), "history": []}

