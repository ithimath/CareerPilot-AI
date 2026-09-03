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
    Priority 1: Random Forest Classification (probability scores, prediction_method="random_forest_classification")
    Priority 2: Rule-based skill/interest matching (existing logic, prediction_method="rule_based")
    Uses Gemini for reasoning text in both cases.
    """
    skills    = student_profile.get("skills", [])
    interests = student_profile.get("interests", [])

    # ── Priority 1: RF Classification ───────────────────────────────────────────
    try:
        from app.ml.model_registry import get_career_model
        rf_model = get_career_model()
        if rf_model.is_trained:
            rf_recs = rf_model.predict_top_n(student_profile, top_n=top_n)
            if rf_recs:
                all_careers = get_careers()
                career_lookup = {c["title"].lower(): c for c in all_careers}

                recommendations = []
                for rf_rec in rf_recs:
                    title = rf_rec["title"]
                    prob  = rf_rec.get("probability_score", 0.0)

                    # Merge with career dataset metadata
                    career_data = career_lookup.get(title.lower(), {})
                    required_skills = career_data.get("required_skills", [])

                    # Compute matching/missing from student's skills
                    student_skills_norm = {_normalize_skill(s) for s in skills}
                    matching = [s for s in required_skills if _normalize_skill(s) in student_skills_norm]
                    missing  = [s for s in required_skills if _normalize_skill(s) not in student_skills_norm]

                    # Gemini reasoning (optional enhancement)
                    try:
                        reason = await generate_career_reasoning(
                            student_profile={"name": student_profile.get("name"),
                                              "skills": skills[:15],
                                              "interests": interests[:10],
                                              "target_career": student_profile.get("target_career")},
                            career_title=title,
                            match_percentage=prob,
                        )
                    except Exception:
                        reason = rf_rec.get("reason", f"RF model predicts {prob:.1f}% match for {title}.")

                    match_pct = round(
                        len(matching) / len(required_skills) * 100, 1
                    ) if required_skills else prob

                    salary_range = career_data.get("salary_range") or "Contact recruiters for current ranges"

                    rec = CareerRecommendation(
                        title=title,
                        match_percentage=match_pct,
                        description=career_data.get("description", ""),
                        required_skills=required_skills,
                        matching_skills=matching,
                        missing_skills=missing[:10],
                        market_demand=career_data.get("market_demand", ""),
                        salary_range=salary_range,
                        reason=reason,
                        category=career_data.get("category", ""),
                        probability_score=prob,
                        recommendation_method="random_forest_classification",
                        recommendation_label="Powered by Random Forest Classification",
                    )
                    recommendations.append(rec)

                logger.info(f"Career RF produced {len(recommendations)} recommendations for uid={uid}")
                return CareerRecommendationResponse(
                    uid=uid,
                    recommendations=recommendations,
                    generated_at=datetime.utcnow(),
                    recommendation_method="random_forest_classification",
                    recommendation_label="Powered by Random Forest Classification",
                )
    except Exception as rf_err:
        logger.debug(f"Career RF unavailable, falling back to rule-based: {rf_err}")

    # ── Priority 2: Rule-based (existing logic) ─────────────────────────────────
    all_careers = get_careers()
    # Score all careers
    scored = []
    for career in all_careers:
        pct, matching, missing = _compute_match(skills, interests, career)
        scored.append((pct, career, matching, missing))
    scored.sort(key=lambda x: x[0], reverse=True)
    top_careers = scored[:top_n]

    recommendations = []
    for pct, career, matching, missing in top_careers:
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
            missing_skills=missing[:10],
            market_demand=career.get("market_demand", ""),
            salary_range=salary_range,
            reason=reason,
            category=career.get("category", ""),
            recommendation_method="rule_based",
            recommendation_label="Matched via Skill Alignment",
        )
        recommendations.append(rec)

    return CareerRecommendationResponse(
        uid=uid,
        recommendations=recommendations,
        generated_at=datetime.utcnow(),
        recommendation_method="rule_based",
        recommendation_label="Matched via Skill Alignment",
    )


def get_skill_gap_for_career(student_skills: List[str], career_title: str) -> dict:
    """
    Compute skill gap between student skills and target career.
    Priority 1: Enhanced skill gap model with priority classification.
    Priority 2: Original rule-based comparison.
    """
    # ── Priority 1: Enhanced skill gap model ───────────────────────────────
    try:
        from app.ml.skill_gap_model import get_enhanced_skill_gap
        result = get_enhanced_skill_gap(student_skills, career_title)
        if not result.get("error"):
            # Supplement with course suggestions from data_service
            from app.services.data_service import get_courses_for_skill
            for item in result.get("missing_skills", []):
                if not item.get("courses"):
                    item["courses"] = get_courses_for_skill(item["skill"])
            return result
    except Exception as e:
        logger.debug(f"Enhanced skill gap unavailable: {e}")

    # ── Priority 2: Original rule-based fallback ──────────────────────────────
    from app.services.data_service import get_courses_for_skill

    career = get_career_by_title(career_title)
    if not career:
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
            "analysis_method": "rule_based_career_mapping",
            "analysis_label":  "Rule-Based Career Mapping",
        }

    required = career.get("required_skills", [])
    student_norm = {s.strip().lower() for s in student_skills}

    matching = []
    missing_items = []
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
                "skill":      skill,
                "importance": importance,
                "priority":   importance,
                "difficulty": difficulty,
                "courses":    courses,
                "status":     "missing",
            })

    completion_pct = (
        round(len(matching) / len(required) * 100, 1) if required else 0.0
    )

    return {
        "target_career":      career["title"],
        "matching_skills":    matching,
        "missing_skills":     missing_items,
        "completion_percentage": completion_pct,
        "total_required":     len(required),
        "total_matching":     len(matching),
        "analysis_method":    "rule_based_career_mapping",
        "analysis_label":     "Rule-Based Career Mapping",
    }
