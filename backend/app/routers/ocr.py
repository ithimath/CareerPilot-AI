"""OCR router — manual re-process endpoint"""
from fastapi import APIRouter, Depends, HTTPException
from app.core.dependencies import get_current_user
from app.core.firebase import get_firestore, get_storage_bucket
from app.schemas.models import CertificateStatus
from app.services.ocr_service import extract_text
from app.services.gemini_service import extract_skills_from_text
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/reprocess/{cert_id}")
async def reprocess_certificate(cert_id: str, user: dict = Depends(get_current_user)):
    """Manually re-trigger OCR and Gemini analysis for a certificate."""
    try:
        db = get_firestore()
        cert_ref = db.collection("certificates").document(cert_id)
        doc = cert_ref.get()

        if not doc.exists:
            raise HTTPException(status_code=404, detail="Certificate not found")

        cert_data = doc.to_dict()
        if cert_data.get("uid") != user["uid"]:
            raise HTTPException(status_code=403, detail="Not authorized")

        # Download from Storage
        bucket = get_storage_bucket()
        blob = bucket.blob(cert_data["storage_path"])
        file_bytes = blob.download_as_bytes()

        # Determine content type from filename
        fname = cert_data.get("file_name", "")
        if fname.endswith(".pdf"):
            content_type = "application/pdf"
        elif fname.endswith(".png"):
            content_type = "image/png"
        else:
            content_type = "image/jpeg"

        cert_ref.update({"status": CertificateStatus.PROCESSING, "processing_error": ""})
        extracted_text, method = extract_text(file_bytes, content_type)
        cert_ref.update({"status": CertificateStatus.TEXT_EXTRACTED, "extracted_text": extracted_text})

        cert_ref.update({"status": CertificateStatus.AI_ANALYZING})
        extracted = await extract_skills_from_text(extracted_text)
        cert_ref.update({
            "status": CertificateStatus.COMPLETED,
            "extracted_skills": extracted.skills.model_dump(),
            "certificate_title": extracted.certificate_title,
            "issuing_organization": extracted.issuing_organization,
        })

        return {"success": True, "message": "Reprocessed successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reprocess failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
