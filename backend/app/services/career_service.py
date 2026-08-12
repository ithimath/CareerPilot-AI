"""
Career Recommendation Service
Scores careers against student profile using skill/interest matching.
"""
import logging
from typing import List, Dict
from datetime import datetime
from app.services.data_service import get_careers, get_career_by_title
from app.services.gemini_service import generate_career_reasoning
from app.schemas.models import CareerRecommendation, CareerRecommendationResponse

logger = logging.getLogger(__name__)


def _normalize_skill(skill: str) -> str:
    return skill.strip().lower()


def _compute_match(student_skills: List[str], student_interests: List[str],
                   career: Dict) -> tuple[float, List[str], List[str]]:
    """
    Compute match % between student and a career.
    Returns (percentage, matching_skills, missing_skills)
    """
    required = career.get("required_skills", [])
    keywords = career.get("keywords", [])

    if not required:
        return 0.0, [], []

    student_skills_norm = {_normalize_skill(s) for s in student_skills}
    student_interests_norm = {_normalize_skill(i) for i in student_interests}

    # Skill match (80% weight)
    matching = []
    missing = []
    for skill in required:
        skill_norm = _normalize_skill(skill)
        if skill_norm in student_skills_norm:
            matching.append(skill)
        else:
            missing.append(skill)

    skill_ratio = len(matching) / len(required) if required else 0

    # Interest match (20% weight)
    interest_bonus = 0.0
    for kw in keywords:
        if kw.lower() in student_interests_norm:
            interest_bonus += 0.05
    interest_bonus = min(interest_bonus, 0.2)

    raw_score = skill_ratio * 0.8 + interest_bonus
    percentage = round(min(raw_score * 100, 100.0), 1)

    return percentage, matching, missing


async def generate_career_recommendations(
    uid: str,
    student_profile: dict,
    top_n: int = 5,
) -> CareerRecommendationResponse:
    """
    Generate top N career recommendations for a student.
    Uses dataset for factual data + Gemini for reasoning text.
    """
    skills = student_profile.get("skills", [])
    interests = student_profile.get("interests", [])
    all_careers = get_careers()

    # Score all careers
    scored = []
    for career in all_careers:
        pct, matching, missing = _compute_match(skills, interests, career)
        scored.append((pct, career, matching, missing))

    # Sort by match %, take top N
    scored.sort(key=lambda x: x[0], reverse=True)
    top_careers = scored[:top_n]

    recommendations = []
    for pct, career, matching, missing in top_careers:
        # Generate reasoning with Gemini (gracefully fall back)
        try:
            reason = await generate_career_reasoning(
                student_profile={"name": student_profile.get("name"),
                                  "skills": skills[:15],
                                  "interests": interests[:10],
                                  "target_career": student_profile.get("target_career")},
                career_title=career["title"],
                match_percentage=pct,
            )
        except Exception as e:
            logger.warning(f"Career reasoning failed for {career['title']}: {e}")
            reason = (
                f"Based on your {len(matching)} matching skills out of "
                f"{len(career.get('required_skills', []))} required, "
                f"{career['title']} is a strong career option."
            )

        salary_range = career.get("salary_range") or (
            f"${career.get('salary_min', 0):,} – ${career.get('salary_max', 0):,}"
            if career.get("salary_min") else "Contact recruiters for current ranges"
        )

        rec = CareerRecommendation(
            title=career["title"],
            match_percentage=pct,
            description=career.get("description", ""),
            required_skills=career.get("required_skills", []),
            matching_skills=matching,
            missing_skills=missing[:10],  # cap at 10 to avoid overwhelming
            market_demand=career.get("market_demand", ""),
            salary_range=salary_range,
            reason=reason,
            category=career.get("category", ""),
        )
        recommendations.append(rec)

    return CareerRecommendationResponse(
        uid=uid,
        recommendations=recommendations,
        generated_at=datetime.utcnow(),
    )


def get_skill_gap_for_career(student_skills: List[str], career_title: str) -> dict:
    """
    Compute skill gap between student skills and target career.
    """
    from app.services.data_service import get_courses_for_skill

    career = get_career_by_title(career_title)
    if not career:
        # Try partial match
        all_careers = get_careers()
        career_title_lower = career_title.lower()
        for c in all_careers:
            if career_title_lower in c.get("title", "").lower():
                career = c
                break

    if not career:
        return {
            "error": f"Career '{career_title}' not found in dataset",
            "matching_skills": [],
            "missing_skills": [],
            "completion_percentage": 0.0,
        }

    required = career.get("required_skills", [])
    student_norm = {s.strip().lower() for s in student_skills}

    matching = []
    missing_items = []

    # Skill importance mapping (first skills in list are usually more critical)
    importance_map = {0: "critical", 1: "critical", 2: "high", 3: "high"}

    for idx, skill in enumerate(required):
        skill_norm = skill.strip().lower()
        if skill_norm in student_norm:
            matching.append(skill)
        else:
            importance = importance_map.get(idx, "medium" if idx < 7 else "low")
            difficulty = "hard" if importance in ("critical", "high") else "medium"
            courses = get_courses_for_skill(skill)
            missing_items.append({
                "skill": skill,
                "importance": importance,
                "difficulty": difficulty,
                "courses": courses,
                "status": "missing",
            })

    completion_pct = (
        round(len(matching) / len(required) * 100, 1) if required else 0.0
    )

    return {
        "target_career": career["title"],
        "matching_skills": matching,
        "missing_skills": missing_items,
        "completion_percentage": completion_pct,
        "total_required": len(required),
        "total_matching": len(matching),
    }
