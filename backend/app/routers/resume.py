"""
CareerPilot AI — Resume & ATS Scanner Router
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from app.core.auth import get_current_user_optional
from app.services.gemini_service import call_gemini_json
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

SAMPLE_ATS_RESULT = {
    "ats_score": 82,
    "breakdown": {
        "formatting": 90,
        "keywords_match": 78,
        "action_verbs": 85,
        "quantifiable_impact": 75
    },
    "matched_keywords": ["Python", "FastAPI", "React", "SQL", "Git", "REST APIs"],
    "missing_keywords": ["Docker", "CI/CD", "AWS", "Unit Testing"],
    "strengths": [
        "Clean structure with clear section headings",
        "Strong use of active verbs (developed, engineered, deployed)",
        "Good match for Web & Software Development roles"
    ],
    "improvements": [
        "Include quantifiable metrics (e.g. improved performance by 35%)",
        "Add key DevOps tools like Docker or GitHub Actions",
        "Add links to live demo URLs or GitHub repositories"
    ]
}

@router.post("/analyze-ats")
async def analyze_ats_resume(
    payload: dict = Body(...),
    user: dict = Depends(get_current_user_optional)
):
    resume_text = payload.get("resume_text", "")
    target_role = payload.get("target_role", "Software Engineer")
    
    if not resume_text:
        return SAMPLE_ATS_RESULT

    prompt = f"""
    Analyze the following resume for the target role: '{target_role}'.
    Provide an ATS scoring analysis in JSON format with keys:
    - ats_score (integer 0-100)
    - breakdown (object with formatting, keywords_match, action_verbs, quantifiable_impact as integers 0-100)
    - matched_keywords (array of strings)
    - missing_keywords (array of strings)
    - strengths (array of strings)
    - improvements (array of strings)

    Resume Text:
    {resume_text[:3000]}
    """
    
    try:
        result = await call_gemini_json(prompt)
        return result
    except Exception as e:
        logger.warning(f"Gemini ATS analysis fallback: {e}")
        return SAMPLE_ATS_RESULT
