"""Certificates router — upload, process, delete with deduplication and replacement"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import Response
from typing import Optional
from app.core.dependencies import get_current_user
from app.core.firebase import get_firestore, get_storage_bucket
from app.schemas.models import CertificateStatus
from app.services.ocr_service import extract_text
from app.services.gemini_service import extract_skills_from_text
from app.services.scoring_service import calculate_job_readiness_score
from datetime import datetime
import uuid
import logging
import os
import re
import hashlib
import mimetypes

router = APIRouter()
logger = logging.getLogger(__name__)


ALLOWED_CERT_TYPES = {
    "application/pdf": ".pdf",
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
}
MAX_CERT_SIZE = 10 * 1024 * 1024  # 10MB


def _normalize_skill(skill: str) -> str:
    return skill.strip().lower()


def _merge_skills(existing: list, new_skills: list) -> list:
    """Merge new skills into existing, preventing duplicates (case-insensitive)."""
    existing_norm = {_normalize_skill(s): s for s in existing}
    for skill in new_skills:
        norm = _normalize_skill(skill)
        if norm and norm not in existing_norm:
            existing_norm[norm] = skill.strip()
    return list(existing_norm.values())


async def _process_certificate(cert_id: str, uid: str, file_bytes: bytes, content_type: str):
    """Background task: OCR → Gemini → Firestore update → score recalc."""
    db = get_firestore()
    cert_ref = db.collection("certificates").document(cert_id)
    profile_ref = db.collection("profiles").document(uid)

    try:
        # Step 1: OCR
        cert_ref.update({"status": CertificateStatus.PROCESSING})
        extracted_text, method = extract_text(file_bytes, content_type)
        cert_ref.update({
            "status": CertificateStatus.TEXT_EXTRACTED,
            "extracted_text": extracted_text,
            "ocr_method": method,
        })

        # Step 2: Gemini skill extraction
        cert_ref.update({"status": CertificateStatus.AI_ANALYZING})
        extracted = await extract_skills_from_text(extracted_text)

        # Flatten all skills into one list
        all_new_skills = []
        for category, skill_list in extracted.skills.model_dump().items():
            all_new_skills.extend(skill_list)

        # Step 3: Update certificate document
        cert_ref.update({
            "status": CertificateStatus.COMPLETED,
            "extracted_skills": extracted.skills.model_dump(),
            "certificate_title": extracted.certificate_title,
            "issuing_organization": extracted.issuing_organization,
        })

        # Step 4: Merge skills into profile
        profile_doc = profile_ref.get()
        if profile_doc.exists:
            profile_data = profile_doc.to_dict()
            existing_skills = profile_data.get("skills", [])
            merged_skills = _merge_skills(existing_skills, all_new_skills)

            # Add cert title to certifications list
            cert_title = extracted.certificate_title or "Certificate"
            existing_certs = profile_data.get("certifications", [])
            if cert_title not in existing_certs:
                existing_certs.append(cert_title)

            profile_ref.update({
                "skills": merged_skills,
                "certifications": existing_certs,
                "updated_at": datetime.utcnow(),
            })

            # Step 5: Recalculate job score
            updated_profile = profile_ref.get().to_dict()
            score = calculate_job_readiness_score(updated_profile)
            db.collection("jobScores").document(uid).set({
                **score.model_dump(),
                "uid": uid,
                "updated_at": datetime.utcnow(),
            })

            logger.info(
                f"Certificate {cert_id} processed. "
                f"Skills: {len(all_new_skills)} new. Score: {score.total_score}"
            )

    except Exception as e:
        logger.error(f"Certificate processing failed for {cert_id}: {e}")
        cert_ref.update({
            "status": CertificateStatus.FAILED,
            "processing_error": str(e),
        })


@router.get("")
async def list_certificates(user: dict = Depends(get_current_user)):
    """List all certificates strictly for the authenticated user."""
    try:
        db = get_firestore()
        docs = (
            db.collection("certificates")
            .where("uid", "==", user["uid"])
            .order_by("upload_date", direction="DESCENDING")
            .stream()
        )
        certs = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            # Convert datetime to ISO string for JSON serialization
            for field in ("upload_date",):
                if field in data and hasattr(data[field], "isoformat"):
                    data[field] = data[field].isoformat()
            certs.append(data)
        return {"certificates": certs}
    except Exception as e:
        logger.error(f"List certificates failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def upload_certificate(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    replace_id: Optional[str] = Form(None),
    user: dict = Depends(get_current_user),
):
    """
    Upload certificate with:
    - Deduplication: checks if this file has already been uploaded by the user.
    - Replacement: if replace_id is supplied, atomically removes old cert and replaces.
    - User isolation: certificates stored strictly under user UID.
    - Private access: files are not made publicly browsable.
    """
    if file.content_type not in ALLOWED_CERT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only PDF, PNG, JPG, JPEG files are allowed",
        )

    file_bytes = await file.read()
    if len(file_bytes) > MAX_CERT_SIZE:
        raise HTTPException(status_code=400, detail="File must be under 10MB")
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="File is empty")

    uid = user["uid"]
    file_hash = hashlib.sha256(file_bytes).hexdigest()

    ext = ALLOWED_CERT_TYPES[file.content_type]
    raw_fname = os.path.basename(file.filename or f"certificate{ext}")
    clean_fname = re.sub(r'[^a-zA-Z0-9_.-]', '_', raw_fname)

    db = get_firestore()

    # 1. Fetch user's existing certificates to check for duplicates and handle replacement
    existing_docs = list(db.collection("certificates").where("uid", "==", uid).stream())
    existing_certs = [d.to_dict() for d in existing_docs]

    old_cert_data = None
    if replace_id:
        old_cert_data = next((c for c in existing_certs if c.get("id") == replace_id), None)
        if not old_cert_data:
            raise HTTPException(status_code=404, detail="Target certificate to replace not found.")
        if old_cert_data.get("uid") != uid:
            raise HTTPException(status_code=403, detail="Not authorized to replace this certificate.")

    # 2. If not an explicit replacement, check for identical duplicates (by SHA-256 hash or filename)
    if not replace_id:
        for existing in existing_certs:
            if existing.get("file_hash") == file_hash or existing.get("file_name") == clean_fname:
                raise HTTPException(
                    status_code=409,
                    detail=f"Certificate '{existing.get('file_name', clean_fname)}' already exists in your account. To update it, please replace the existing certificate."
                )

    # 3. If replacing, safely clean up old file from storage and delete old Firestore doc
    if old_cert_data:
        try:
            bucket = get_storage_bucket()
            old_blob = bucket.blob(old_cert_data.get("storage_path", ""))
            if old_blob.exists():
                old_blob.delete()
        except Exception as e:
            logger.warning(f"Storage delete failed during replacement: {e}")
        db.collection("certificates").document(replace_id).delete()

    cert_id = str(uuid.uuid4())
    storage_path = f"certificates/{uid}/{cert_id}/{clean_fname}"

    try:
        # Upload to Storage (kept private for authenticated user only)
        bucket = get_storage_bucket()
        blob = bucket.blob(storage_path)
        blob.upload_from_string(file_bytes, content_type=file.content_type)
        # Note: Do NOT call blob.make_public() to preserve privacy

        file_url = f"/api/certificates/{cert_id}/file"

        # Create Firestore metadata doc
        cert_data = {
            "id": cert_id,
            "uid": uid,
            "file_name": clean_fname,
            "file_url": file_url,
            "storage_path": storage_path,
            "file_hash": file_hash,
            "file_size": len(file_bytes),
            "upload_date": datetime.utcnow(),
            "status": CertificateStatus.UPLOADED,
            "extracted_text": "",
            "extracted_skills": {},
            "certificate_title": "",
            "issuing_organization": "",
            "processing_error": "",
            "ocr_method": "",
        }
        db.collection("certificates").document(cert_id).set(cert_data)

        # Trigger async processing
        background_tasks.add_task(
            _process_certificate, cert_id, uid, file_bytes, file.content_type
        )

        return {
            "success": True,
            "certificate_id": cert_id,
            "file_url": file_url,
            "replaced_id": replace_id,
            "status": CertificateStatus.UPLOADED,
            "message": "Certificate uploaded. Processing started in background." if not replace_id else "Certificate replaced successfully. Processing started.",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Certificate upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{cert_id}")
async def delete_certificate(cert_id: str, user: dict = Depends(get_current_user)):
    """Delete a certificate from Storage and Firestore."""
    try:
        db = get_firestore()
        cert_ref = db.collection("certificates").document(cert_id)
        doc = cert_ref.get()

        if not doc.exists:
            raise HTTPException(status_code=404, detail="Certificate not found")

        cert_data = doc.to_dict()
        if cert_data.get("uid") != user["uid"]:
            raise HTTPException(status_code=403, detail="Not authorized")

        # Delete from Storage
        try:
            bucket = get_storage_bucket()
            blob = bucket.blob(cert_data.get("storage_path", ""))
            if blob.exists():
                blob.delete()
        except Exception as e:
            logger.warning(f"Storage delete failed (non-critical): {e}")

        # Delete from Firestore
        cert_ref.delete()

        # Recalculate job score upon certificate deletion to maintain data integrity
        uid = user["uid"]
        try:
            profile_ref = db.collection("profiles").document(uid)
            profile_doc = profile_ref.get()
            if profile_doc.exists:
                profile_data = profile_doc.to_dict()
                cert_title = cert_data.get("certificate_title")
                if cert_title and cert_title in profile_data.get("certifications", []):
                    profile_data["certifications"].remove(cert_title)
                    profile_ref.update({"certifications": profile_data["certifications"]})
                score = calculate_job_readiness_score(profile_data)
                db.collection("jobScores").document(uid).set({
                    **score.model_dump(),
                    "uid": uid,
                    "updated_at": datetime.utcnow(),
                })
        except Exception as e:
            logger.warning(f"Score recalculation after cert delete warning: {e}")

        return {"success": True, "message": "Certificate deleted and readiness score recalculated."}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete certificate failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{cert_id}")
async def get_certificate(cert_id: str, user: dict = Depends(get_current_user)):
    """Get a single certificate's details — strictly for authenticated owner."""
    try:
        db = get_firestore()
        doc = db.collection("certificates").document(cert_id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Certificate not found")
        data = doc.to_dict()
        if data.get("uid") != user["uid"]:
            raise HTTPException(status_code=403, detail="Not authorized")
        data["id"] = doc.id
        return data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get certificate failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{cert_id}/file")
async def get_certificate_file(cert_id: str, user: dict = Depends(get_current_user)):
    """Stream/download certificate file securely — strictly for authenticated owner."""
    try:
        db = get_firestore()
        doc = db.collection("certificates").document(cert_id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Certificate not found")
        data = doc.to_dict()
        if data.get("uid") != user["uid"]:
            raise HTTPException(status_code=403, detail="Not authorized")

        bucket = get_storage_bucket()
        blob = bucket.blob(data.get("storage_path", ""))
        if not blob.exists():
            raise HTTPException(status_code=404, detail="Certificate file not found in storage")

        file_bytes = blob.download_as_bytes()
        media_type, _ = mimetypes.guess_type(data.get("file_name", "certificate.pdf"))
        return Response(content=file_bytes, media_type=media_type or "application/pdf")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download certificate file failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
