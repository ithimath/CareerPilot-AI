"""Profile router — CRUD operations for student profile"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.core.dependencies import get_current_user
from app.core.firebase import get_firestore, get_storage_bucket
from app.schemas.models import ProfileUpdateRequest, SuccessResponse
from app.services.scoring_service import calculate_job_readiness_score, calculate_profile_completion
from datetime import datetime
import uuid
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/jpg", "image/webp"}
MAX_PROFILE_IMG_SIZE = 5 * 1024 * 1024  # 5MB


@router.get("")
async def get_profile(user: dict = Depends(get_current_user)):
    """Fetch the student's full profile."""
    try:
        db = get_firestore()
        doc = db.collection("profiles").document(user["uid"]).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Profile not found")
        profile = doc.to_dict()
        # Add computed fields
        completion = calculate_profile_completion(profile)
        profile["profile_completion"] = completion
        return profile
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get profile failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("")
async def update_profile(
    data: ProfileUpdateRequest,
    user: dict = Depends(get_current_user),
):
    """Update profile fields and recalculate job score."""
    try:
        db = get_firestore()
        uid = user["uid"]
        profile_ref = db.collection("profiles").document(uid)

        update_data = data.model_dump(exclude_none=True)
        update_data["updated_at"] = datetime.utcnow().isoformat()

        # Clean nested lists
        if "projects" in update_data:
            update_data["projects"] = [
                p.model_dump() if hasattr(p, "model_dump") else p
                for p in update_data["projects"]
            ]
        if "internships" in update_data:
            update_data["internships"] = [
                i.model_dump() if hasattr(i, "model_dump") else i
                for i in update_data["internships"]
            ]

        # Use set with merge=True for robust document creation/update
        profile_ref.set(update_data, merge=True)

        # Recalculate job readiness score
        full_profile_doc = profile_ref.get()
        full_profile = full_profile_doc.to_dict() if full_profile_doc.exists else {"uid": uid, **update_data}
        full_profile["uid"] = uid

        score = calculate_job_readiness_score(full_profile)
        db.collection("jobScores").document(uid).set({
            **score.model_dump(),
            "uid": uid,
            "updated_at": datetime.utcnow().isoformat(),
        })

        completion = calculate_profile_completion(full_profile)
        return {
            "success": True,
            "message": "Candidate Dossier updated successfully",
            "job_score": score.total_score,
            "profile_completion": completion,
        }
    except Exception as e:
        logger.error(f"Update profile failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/picture")
async def upload_profile_picture(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
):
    """Upload profile picture to Firebase Storage."""
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Only JPEG and PNG images are allowed")

    file_bytes = await file.read()
    if len(file_bytes) > MAX_PROFILE_IMG_SIZE:
        raise HTTPException(status_code=400, detail="Image must be under 5MB")

    try:
        uid = user["uid"]
        ext = file.filename.rsplit(".", 1)[-1].lower()
        storage_path = f"profile_pictures/{uid}/profile.{ext}"

        bucket = get_storage_bucket()
        blob = bucket.blob(storage_path)
        blob.upload_from_string(file_bytes, content_type=file.content_type)
        blob.make_public()
        url = blob.public_url

        db = get_firestore()
        db.collection("profiles").document(uid).update({
            "profile_picture_url": url,
            "updated_at": datetime.utcnow(),
        })

        return {"success": True, "url": url}

    except Exception as e:
        logger.error(f"Profile picture upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/completion")
async def get_profile_completion(user: dict = Depends(get_current_user)):
    """Get profile completion percentage and missing fields."""
    try:
        db = get_firestore()
        doc = db.collection("profiles").document(user["uid"]).get()
        if not doc.exists:
            return {"percentage": 0.0, "missing_fields": [], "is_complete": False}
        return calculate_profile_completion(doc.to_dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
