"""
CareerPilot AI — Resume & ATS Diagnostic Router
Powered by production-grade ResumeAnalyzer service.
"""
from fastapi import APIRouter, Depends, HTTPException, Body, File, UploadFile, Form
from app.core.dependencies import get_current_user_optional
from app.services.resume_analysis_service import ResumeAnalyzer, parse_resume_document
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Global analyzer instance
_analyzer = ResumeAnalyzer()


@router.post("/analyze-ats")
async def analyze_ats_resume(
    payload: dict = Body(...),
    user: dict = Depends(get_current_user_optional)
):
    resume_text = payload.get("resume_text", "").strip()
    target_role = payload.get("target_role", "Software Engineer")
    
    if not resume_text:
        sample_text = "React TypeScript Python SQL Node.js Git FastAPI Docker REST APIs"
        result = _analyzer.analyze(sample_text, target_role)
        return result

    # Execute deterministic ResumeAnalyzer pipeline
    result = _analyzer.analyze(resume_text, target_role)

    # Persist resume version & update readiness score
    uid = user.get("uid") if user else None
    if uid and result:
        try:
            from app.core.firebase import get_firestore
            from app.services.scoring_service import calculate_job_readiness_score

            db = get_firestore()
            version_id = f"v_{int(datetime.utcnow().timestamp())}"
            version_data = {
                "id": str(uuid.uuid4()),
                "version_id": version_id,
                "target_role": target_role,
                "ats_score": result.get("ats_score", 15),
                "score": result.get("score", 15),
                "weighted_breakdown": result.get("weighted_breakdown", {}),
                "matched_keywords": result.get("matching_keywords", []),
                "missing_keywords": result.get("missing_keywords", []),
                "strengths": result.get("strengths", []),
                "improvements": result.get("improvements", []),
                "skill_match_details": result.get("skill_match_details", {}),
                "timestamp": datetime.utcnow().isoformat(),
            }
            db.collection(f"resumes/{uid}/versions").document(version_id).set(version_data)

            # Recalculate score
            profile_doc = db.collection("profiles").document(uid).get()
            profile = profile_doc.to_dict() if profile_doc.exists else {"uid": uid}
            profile["uid"] = uid
            readiness = calculate_job_readiness_score(profile, action_reason="Resume ATS Audit Executed")
            db.collection("jobScores").document(uid).set({
                **readiness.model_dump(),
                "uid": uid,
                "updated_at": datetime.utcnow().isoformat(),
            })
            result["readiness_score"] = readiness.total_score
        except Exception as e:
            logger.warning(f"Failed to persist resume version: {e}")

    return result


@router.post("/upload-ats")
async def upload_ats_resume(
    file: UploadFile = File(...),
    target_role: str = Form("Software Engineer"),
    user: dict = Depends(get_current_user_optional)
):
    """Parse document file (PDF, DOCX, TXT) and run ATS diagnostic."""
    try:
        content = await file.read()
        extracted_text = parse_resume_document(content, file.filename or "resume.pdf")

        if not extracted_text or len(extracted_text.strip()) < 10:
            raise HTTPException(status_code=400, detail="Could not extract readable text from uploaded file.")

        result = _analyzer.analyze(extracted_text, target_role)
        result["extracted_text"] = extracted_text

        # Persist version if authenticated
        uid = user.get("uid") if user else None
        if uid and result:
            try:
                from app.core.firebase import get_firestore
                from app.services.scoring_service import calculate_job_readiness_score

                db = get_firestore()
                version_id = f"v_{int(datetime.utcnow().timestamp())}"
                version_data = {
                    "id": str(uuid.uuid4()),
                    "version_id": version_id,
                    "file_name": file.filename,
                    "target_role": target_role,
                    "ats_score": result.get("ats_score", 15),
                    "score": result.get("score", 15),
                    "weighted_breakdown": result.get("weighted_breakdown", {}),
                    "matched_keywords": result.get("matching_keywords", []),
                    "missing_keywords": result.get("missing_keywords", []),
                    "strengths": result.get("strengths", []),
                    "improvements": result.get("improvements", []),
                    "timestamp": datetime.utcnow().isoformat(),
                }
                db.collection(f"resumes/{uid}/versions").document(version_id).set(version_data)
            except Exception as e:
                logger.warning(f"Failed to persist uploaded resume version: {e}")

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Resume file upload processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process resume file: {str(e)}")


@router.get("/history")
async def get_resume_history(user: dict = Depends(get_current_user_optional)):
    """Fetch previous resume scans for user."""
    uid = user.get("uid", "dev-user-id")
    try:
        from app.core.firebase import get_firestore
        db = get_firestore()
        docs = db.collection(f"resumes/{uid}/versions").stream()
        results = [d.to_dict() for d in docs if d.to_dict()]
        return {"uid": uid, "versions": results}
    except Exception as e:
        logger.error(f"Failed to fetch resume history: {e}")
        return {"uid": uid, "versions": []}



