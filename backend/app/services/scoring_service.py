"""
Job Readiness Score Engine — Deterministic scoring (NO Gemini)
Maximum score = 100 points
"""
import math
import logging
from typing import List, Dict
from app.schemas.models import ScoreBreakdown, ProjectItem, InternshipItem

logger = logging.getLogger(__name__)

# ── Scoring weights ────────────────────────────────────────────────────────────
MAX_SKILLS       = 30
MAX_PROJECTS     = 25
MAX_INTERNSHIPS  = 20
MAX_CERTIFICATES = 10
MAX_PROFILE      = 15
TOTAL_MAX        = 100

# ── Thresholds ─────────────────────────────────────────────────────────────────
SKILLS_SATURATION      = 25   # 25+ skills = full marks
PROJECTS_SATURATION    = 6    # 6+ quality projects = full marks
INTERNSHIPS_SATURATION = 3    # 3+ internships = full marks
CERTS_SATURATION       = 5    # 5+ certificates = full marks

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


def _skills_score(skills: List[str]) -> float:
    """
    Log-scale score for skills:
    - 0 skills → 0
    - 10 skills → ~18
    - 25+ skills → 30 (saturated)
    """
    n = len(skills)
    if n == 0:
        return 0.0
    # Use log scale: score = MAX * log(n+1) / log(SATURATION+1)
    score = MAX_SKILLS * math.log(n + 1) / math.log(SKILLS_SATURATION + 1)
    return round(min(score, float(MAX_SKILLS)), 2)


def _projects_score(projects: List[Dict]) -> float:
    """
    Quality-weighted project score.
    Each project earns up to 1 quality point based on completeness.
    """
    if not projects:
        return 0.0

    total_quality = 0.0
    for p in projects:
        quality = 0.0
        if isinstance(p, dict):
            if p.get("title"):            quality += 0.3
            if p.get("description"):      quality += 0.3
            if p.get("technologies"):     quality += 0.2
            if p.get("github_url"):       quality += 0.1
            if p.get("live_url"):         quality += 0.1
        else:  # ProjectItem
            if p.title:                   quality += 0.3
            if p.description:             quality += 0.3
            if p.technologies:            quality += 0.2
            if p.github_url:              quality += 0.1
            if p.live_url:                quality += 0.1
        total_quality += quality

    # Saturate at PROJECTS_SATURATION quality points
    ratio = min(total_quality / PROJECTS_SATURATION, 1.0)
    return round(ratio * MAX_PROJECTS, 2)


def _internships_score(internships: List[Dict]) -> float:
    """Score internships — each internship earns points for completeness."""
    if not internships:
        return 0.0

    total_quality = 0.0
    for i in internships:
        quality = 0.0
        if isinstance(i, dict):
            if i.get("company"):      quality += 0.4
            if i.get("role"):         quality += 0.3
            if i.get("description"): quality += 0.2
            if i.get("duration"):    quality += 0.1
        else:
            if i.company:            quality += 0.4
            if i.role:               quality += 0.3
            if i.description:        quality += 0.2
            if i.duration:           quality += 0.1
        total_quality += quality

    ratio = min(total_quality / INTERNSHIPS_SATURATION, 1.0)
    return round(ratio * MAX_INTERNSHIPS, 2)


def _certificates_score(certs: List[str]) -> float:
    """Simple count-based certificate score."""
    n = len(certs)
    if n == 0:
        return 0.0
    ratio = min(n / CERTS_SATURATION, 1.0)
    return round(ratio * MAX_CERTIFICATES, 2)


def _profile_completion_score(profile: dict) -> tuple[float, float]:
    """
    Calculate profile completion % and corresponding score.
    Returns (completion_percentage, score)
    """
    total_fields = len(PROFILE_REQUIRED_FIELDS) + len(PROFILE_ARRAY_FIELDS)
    filled = 0

    for field in PROFILE_REQUIRED_FIELDS:
        val = profile.get(field)
        if val and str(val).strip():
            filled += 1

    for field, min_count in PROFILE_ARRAY_FIELDS:
        val = profile.get(field, [])
        if isinstance(val, list) and len(val) >= min_count:
            filled += 1

    completion_pct = round((filled / total_fields) * 100, 1)
    score = round((completion_pct / 100) * MAX_PROFILE, 2)
    return completion_pct, score


def _generate_suggestions(breakdown: dict) -> List[str]:
    """Generate improvement suggestions from weakest areas."""
    suggestions = []
    ratios = {
        "skills":       (breakdown["skills_score"],       MAX_SKILLS),
        "projects":     (breakdown["projects_score"],     MAX_PROJECTS),
        "internships":  (breakdown["internships_score"],  MAX_INTERNSHIPS),
        "certificates": (breakdown["certificates_score"], MAX_CERTIFICATES),
        "profile":      (breakdown["profile_score"],      MAX_PROFILE),
    }

    suggestion_templates = {
        "skills": (
            0.5, "Add more technical skills to your profile. "
                  "Aim for at least 15–25 skills to maximize your score."
        ),
        "projects": (
            0.6, "Build more projects and add detailed descriptions, "
                  "GitHub links, and tech stacks."
        ),
        "internships": (
            0.5, "Apply for internships to gain industry experience. "
                  "Even virtual internships count."
        ),
        "certificates": (
            0.6, "Earn industry certifications (Google, AWS, Coursera) "
                  "to boost your credibility."
        ),
        "profile": (
            0.7, "Complete your profile — add GitHub, LinkedIn, portfolio URL, "
                  "and fill all academic details."
        ),
    }

    # Sort by worst ratio first
    sorted_areas = sorted(ratios.items(), key=lambda x: x[1][0] / x[1][1])
    for area, (score, max_score) in sorted_areas:
        ratio = score / max_score
        threshold, message = suggestion_templates[area]
        if ratio < threshold:
            suggestions.append(message)
        if len(suggestions) >= 3:
            break

    return suggestions


def calculate_job_readiness_score(profile: dict) -> ScoreBreakdown:
    """
    Main scoring function. Uses ML-based vector prediction engine
    (TF-IDF skill alignment + Project tech fit + Experience depth).
    """
    try:
        from app.services.ml_scoring_service import get_ml_predictor
        predictor = get_ml_predictor()
        score_result = predictor.predict_readiness(profile)
        logger.info(
            f"ML Job score for uid={profile.get('uid', '?')}: "
            f"total={score_result.total_score} | skills={score_result.skills_score} | "
            f"target={profile.get('target_career', 'Not specified')}"
        )
        return score_result
    except Exception as e:
        logger.warning(f"ML Scoring failed ({e}) — utilizing fallback scoring pipeline")

    skills_score       = _skills_score(profile.get("skills", []))
    projects_score     = _projects_score(profile.get("projects", []))
    internships_score  = _internships_score(profile.get("internships", []))
    certs_score        = _certificates_score(profile.get("certifications", []))
    completion_pct, profile_score = _profile_completion_score(profile)

    total = round(
        skills_score + projects_score + internships_score + certs_score + profile_score,
        2
    )
    total = min(total, float(TOTAL_MAX))

    breakdown = {
        "skills_score":       skills_score,
        "projects_score":     projects_score,
        "internships_score":  internships_score,
        "certificates_score": certs_score,
        "profile_score":      profile_score,
        "total_score":        total,
    }

    suggestions = _generate_suggestions(breakdown)

    logger.info(
        f"Fallback Job score for uid={profile.get('uid', '?')}: "
        f"total={total} | skills={skills_score} | projects={projects_score}"
    )

    return ScoreBreakdown(**breakdown, suggestions=suggestions)


def calculate_profile_completion(profile: dict) -> dict:
    """Return profile completion metadata for the frontend."""
    pct, _ = _profile_completion_score(profile)

    missing = []
    for field in PROFILE_REQUIRED_FIELDS:
        val = profile.get(field)
        if not val or not str(val).strip():
            missing.append(field.replace("_", " ").replace(" url", " URL").title())

    for field, min_count in PROFILE_ARRAY_FIELDS:
        val = profile.get(field, [])
        if not isinstance(val, list) or len(val) < min_count:
            missing.append(
                f"{field.replace('_', ' ').title()} (at least {min_count})"
            )

    return {
        "percentage": pct,
        "missing_fields": missing,
        "is_complete": pct >= 100.0,
    }
