"""
Job Readiness Score Engine — Multi-Signal Evaluator & History Tracker
Maximum score = 100 points
"""
import math
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.schemas.models import ScoreBreakdown, ScoreHistoryEntry

logger = logging.getLogger(__name__)

# Scoring weights
MAX_SKILLS       = 25.0
MAX_PROJECTS     = 20.0
MAX_INTERVIEWS   = 20.0
MAX_RESUME       = 15.0
MAX_ASSESSMENTS  = 10.0
MAX_CERTIFICATES = 10.0
TOTAL_MAX        = 100.0

# Profile completion required fields
PROFILE_REQUIRED_FIELDS = [
    "name", "college", "degree", "department", "current_year",
    "cgpa", "github_url", "linkedin_url", "portfolio_url",
]

PROFILE_ARRAY_FIELDS = [
    ("skills", 3),         # need at least 3
    ("interests", 2),      # need at least 2
    ("projects", 1),       # need at least 1
    ("internships", 1),    # need at least 1
    ("certifications", 1), # need at least 1
]


def load_user_activities(uid: str) -> Dict[str, List[Dict[str, Any]]]:
    """Fetch user activity records from Firestore / persistent datastore."""
    if not uid:
        return {"interviews": [], "resumes": [], "assessments": [], "certificates": []}

    try:
        from app.core.firebase import get_firestore
        db = get_firestore()

        # 1. Interviews
        interviews = []
        try:
            int_docs = db.collection(f"interviews/{uid}/sessions").stream()
            for doc in int_docs:
                d = doc.to_dict()
                if d: interviews.append(d)
        except Exception:
            pass

        # 2. Resumes
        resumes = []
        try:
            res_docs = db.collection(f"resumes/{uid}/versions").stream()
            for doc in res_docs:
                d = doc.to_dict()
                if d: resumes.append(d)
        except Exception:
            pass

        # 3. Assessments
        assessments = []
        try:
            ass_docs = db.collection(f"assessments/{uid}/records").stream()
            for doc in ass_docs:
                d = doc.to_dict()
                if d: assessments.append(d)
        except Exception:
            pass

        # 4. Certificates
        certificates = []
        try:
            cert_docs = db.collection("certificates").stream()
            for doc in cert_docs:
                d = doc.to_dict() or {}
                if d.get("uid") == uid:
                    certificates.append(d)
        except Exception:
            pass

        return {
            "interviews": interviews,
            "resumes": resumes,
            "assessments": assessments,
            "certificates": certificates,
        }
    except Exception as e:
        logger.warning(f"Failed to load activities for uid={uid}: {e}")
        return {"interviews": [], "resumes": [], "assessments": [], "certificates": []}


def calculate_job_readiness_score(
    profile: dict,
    activities: Optional[Dict[str, Any]] = None,
    action_reason: str = "Profile updated"
) -> ScoreBreakdown:
    """
    Main scoring function. Loads user activity signals and calculates the
    comprehensive 6-dimensional ML readiness score with history tracking.
    """
    uid = profile.get("uid", "")

    if activities is None and uid:
        activities = load_user_activities(uid)
    elif activities is None:
        activities = {}

    try:
        from app.services.ml_scoring_service import get_ml_predictor
        predictor = get_ml_predictor()
        score_result = predictor.predict_readiness(
            profile=profile,
            interviews=activities.get("interviews", []),
            resumes=activities.get("resumes", []),
            assessments=activities.get("assessments", []),
            certificates=activities.get("certificates", []),
        )

        # Load and append history if UID is present
        if uid:
            history = _manage_score_history(uid, score_result, action_reason)
            score_result.history = history

        logger.info(
            f"ML Job score for uid={uid}: "
            f"total={score_result.total_score} | skills={score_result.skills_score} | "
            f"interviews={score_result.interviews_score} | resume={score_result.resume_score}"
        )
        return score_result
    except Exception as e:
        logger.error(f"ML Scoring error ({e}) — falling back to deterministic calculation", exc_info=True)

    # Fallback calculation
    skills_score = min(len(profile.get("skills", [])) * 2.0, MAX_SKILLS)
    projects_score = min(len(profile.get("projects", [])) * 6.0, MAX_PROJECTS)
    interviews_score = min(len(activities.get("interviews", [])) * 6.0, MAX_INTERVIEWS)
    resume_score = 8.0 if (activities.get("resumes") or profile.get("github_url")) else 0.0
    assessments_score = min(len(activities.get("assessments", [])) * 4.0, MAX_ASSESSMENTS)
    certs_score = min(len(profile.get("certifications", [])) * 4.0, MAX_CERTIFICATES)

    total = min(
        round(skills_score + projects_score + interviews_score + resume_score + assessments_score + certs_score, 1),
        TOTAL_MAX
    )

    fallback_breakdown = ScoreBreakdown(
        uid=uid,
        skills_score=skills_score,
        projects_score=projects_score,
        interviews_score=interviews_score,
        resume_score=resume_score,
        assessments_score=assessments_score,
        certificates_score=certs_score,
        total_score=total,
        confidence_level="Standard Grounding",
        data_quality_notice="Calculated via fallback engine.",
        suggestions=["Add technical skills and project descriptions to increase evaluation precision."],
        updated_at=datetime.utcnow().isoformat()
    )
    return fallback_breakdown


def _manage_score_history(uid: str, score_result: ScoreBreakdown, reason: str) -> List[ScoreHistoryEntry]:
    """Retrieve score history, append new entry if changed or on action, and persist."""
    try:
        from app.core.firebase import get_firestore
        db = get_firestore()
        history_doc = db.collection("readinessHistory").document(uid).get()
        entries = []
        if history_doc.exists:
            raw_entries = history_doc.to_dict().get("history", [])
            for e in raw_entries:
                try:
                    entries.append(ScoreHistoryEntry(**e))
                except Exception:
                    pass

        # Check if score changed from last recorded entry
        last_score = entries[-1].total_score if entries else 0.0
        delta = round(score_result.total_score - last_score, 1)

        # Create new history entry
        new_entry = ScoreHistoryEntry(
            timestamp=datetime.utcnow().isoformat(),
            total_score=score_result.total_score,
            delta=delta,
            reason=reason if entries else "Initial Evaluation",
            category_breakdown={
                "skills": score_result.skills_score,
                "projects": score_result.projects_score,
                "interviews": score_result.interviews_score,
                "resume": score_result.resume_score,
                "assessments": score_result.assessments_score,
                "certificates": score_result.certificates_score,
            }
        )

        # Only append if delta != 0 or history is empty or specific action triggered
        if not entries or delta != 0.0 or len(entries) < 2:
            entries.append(new_entry)
            # Keep max last 20 history entries
            if len(entries) > 20:
                entries = entries[-20:]

            db.collection("readinessHistory").document(uid).set({
                "uid": uid,
                "history": [e.model_dump() for e in entries],
                "updated_at": datetime.utcnow().isoformat()
            })

        return entries
    except Exception as e:
        logger.warning(f"Failed to manage score history for uid={uid}: {e}")
        return []


def calculate_profile_completion(profile: dict) -> dict:
    """Return profile completion metadata for the frontend."""
    total_fields = len(PROFILE_REQUIRED_FIELDS) + len(PROFILE_ARRAY_FIELDS)
    filled = 0

    missing = []
    for field in PROFILE_REQUIRED_FIELDS:
        val = profile.get(field)
        if val and str(val).strip():
            filled += 1
        else:
            missing.append(field.replace("_", " ").replace(" url", " URL").title())

    for field, min_count in PROFILE_ARRAY_FIELDS:
        val = profile.get(field, [])
        if isinstance(val, list) and len(val) >= min_count:
            filled += 1
        else:
            missing.append(
                f"{field.replace('_', ' ').title()} (at least {min_count})"
            )

    completion_pct = round((filled / total_fields) * 100, 1)
    return {
        "percentage": completion_pct,
        "missing_fields": missing,
        "is_complete": completion_pct >= 100.0,
    }

