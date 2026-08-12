"""Careers router — recommendations and target career"""
from fastapi import APIRouter, Depends, HTTPException
from app.core.dependencies import get_current_user
from app.core.firebase import get_firestore
from app.services.career_service import generate_career_recommendations
from app.services.data_service import get_careers
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/recommendations")
async def get_career_recommendations(user: dict = Depends(get_current_user)):
    """
    Get top 5 career recommendations.
    Uses cached Firestore result if less than 1 hour old, else regenerates.
    """
    try:
        db = get_firestore()
        uid = user["uid"]

        # Check cache
        cached_doc = db.collection("careerRecommendations").document(uid).get()
        if cached_doc.exists:
            cached = cached_doc.to_dict()
            generated_at = cached.get("generated_at")
            if generated_at:
                # Use cache if less than 1 hour old
                age = (datetime.utcnow() - generated_at.replace(tzinfo=None)).seconds
                if age < 3600:
                    return cached

        # Generate fresh recommendations
        profile_doc = db.collection("profiles").document(uid).get()
        if not profile_doc.exists:
            raise HTTPException(status_code=404, detail="Profile not found")

        profile = profile_doc.to_dict()
        result = await generate_career_recommendations(uid, profile)

        # Cache in Firestore
        result_dict = result.model_dump()
        # Convert datetime for Firestore
        result_dict["generated_at"] = datetime.utcnow()
        db.collection("careerRecommendations").document(uid).set(result_dict)

        return result_dict

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Career recommendations failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommendations/refresh")
async def refresh_career_recommendations(user: dict = Depends(get_current_user)):
    """Force regenerate career recommendations."""
    try:
        db = get_firestore()
        uid = user["uid"]

        profile_doc = db.collection("profiles").document(uid).get()
        if not profile_doc.exists:
            raise HTTPException(status_code=404, detail="Profile not found")

        profile = profile_doc.to_dict()
        result = await generate_career_recommendations(uid, profile)
        result_dict = result.model_dump()
        result_dict["generated_at"] = datetime.utcnow()
        db.collection("careerRecommendations").document(uid).set(result_dict)
        return result_dict

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/target")
async def set_target_career(data: dict, user: dict = Depends(get_current_user)):
    """Set the user's target career."""
    career_title = data.get("career_title", "").strip()
    if not career_title:
        raise HTTPException(status_code=400, detail="career_title is required")
    try:
        db = get_firestore()
        uid = user["uid"]
        db.collection("profiles").document(uid).update({
            "target_career": career_title,
            "updated_at": datetime.utcnow(),
        })
        return {"success": True, "target_career": career_title}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_all_careers(user: dict = Depends(get_current_user)):
    """Return all available careers from the dataset."""
    try:
        careers = get_careers()
        return {"careers": [{"title": c["title"], "category": c.get("category", "")} for c in careers]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
