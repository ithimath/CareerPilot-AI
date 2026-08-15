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
    Get current persistent career readiness score for authenticated UID.
    - If user has previously saved score, return it along with progression history.
    - If user has active data (skills, projects, interviews, tests, resume), recalculate and save.
    - If brand new account with 0 activities, returns initial 0.0 baseline score.
    """
    try:
        db = get_firestore()
        uid = user["uid"]

        # Check existing saved score
        doc = db.collection("jobScores").document(uid).get()
        if doc.exists:
            score_data = doc.to_dict()
            # Also attach history
            history_doc = db.collection("readinessHistory").document(uid).get()
            if history_doc.exists:
                score_data["history"] = history_doc.to_dict().get("history", [])
            return score_data

        # Check if user has populated profile or any activities
        profile_doc = db.collection("profiles").document(uid).get()
        activities = load_user_activities(uid)
        has_profile_data = profile_doc.exists and (
            bool(profile_doc.to_dict().get("skills")) or
            bool(profile_doc.to_dict().get("projects")) or
            bool(profile_doc.to_dict().get("certifications"))
        )
        has_activity_data = (
            bool(activities.get("interviews")) or
            bool(activities.get("resumes")) or
            bool(activities.get("assessments")) or
            bool(activities.get("certificates"))
        )

        if has_profile_data or has_activity_data:
            return await recalculate_job_score(user)

        # Brand new user initial 0 score
        initial_score = {
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
            "data_quality_notice": "New candidate account. Complete activities such as adding technical skills, taking mock tests, or running ATS resume diagnostics to compute your score.",
            "positive_drivers": [],
            "suggestions": [
                "Welcome to CareerPilot AI! Add 3+ technical skills with proficiency in your profile.",
                "Execute a resume ATS diagnostic scan to audit parser compliance.",
                "Take a technical mock test or start an AI Mock Interview.",
            ],
            "max_scores": {
                "skills": 25,
                "projects": 20,
                "interviews": 20,
                "resume": 15,
                "assessments": 10,
                "certificates": 10,
            },
            "history": [],
            "updated_at": datetime.utcnow().isoformat(),
        }

        db.collection("jobScores").document(uid).set(initial_score)
        return initial_score

    except Exception as e:
        logger.error(f"Failed to fetch job score for uid={user.get('uid')}: {e}", exc_info=True)
        return {
            "uid": user.get("uid", "user_new"),
            "total_score": 0.0,
            "skills_score": 0.0,
            "projects_score": 0.0,
            "interviews_score": 0.0,
            "resume_score": 0.0,
            "assessments_score": 0.0,
            "certificates_score": 0.0,
            "profile_score": 0.0,
            "internships_score": 0.0,
            "suggestions": [
                "Welcome to CareerPilot AI! Complete candidate activities to calculate your Career Readiness Score."
            ],
            "history": [],
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

