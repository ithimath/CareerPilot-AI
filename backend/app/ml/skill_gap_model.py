"""
Skill Gap Analysis — Classification + Rule-Based
Enhanced skill gap analysis combining deterministic career-skill mapping
with ML-informed priority classification.
Clearly labeled as "Rule-Based Career Mapping" (not ML predictions).
"""
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# ── Authoritative Career → Required Skills Mapping ────────────────────────────
# This is deterministic and rule-based (NOT ML). It is the ground truth
# for what skills each career requires, ordered by importance.
CAREER_SKILL_REQUIREMENTS: Dict[str, List[Dict[str, Any]]] = {
    "AI / Machine Learning Engineer": [
        {"skill": "Python",            "priority": "critical",     "category": "Language",    "time_weeks": 12, "description": "Primary language for ML/AI development"},
        {"skill": "Machine Learning",  "priority": "critical",     "category": "Core Concept","time_weeks": 16, "description": "Fundamental ML algorithms and theory"},
        {"skill": "Deep Learning",     "priority": "critical",     "category": "Core Concept","time_weeks": 12, "description": "Neural networks, CNNs, RNNs"},
        {"skill": "TensorFlow",        "priority": "high",         "category": "Framework",   "time_weeks": 8,  "description": "Industry-standard ML framework"},
        {"skill": "PyTorch",           "priority": "high",         "category": "Framework",   "time_weeks": 8,  "description": "Research-focused deep learning framework"},
        {"skill": "Scikit-Learn",      "priority": "high",         "category": "Library",     "time_weeks": 4,  "description": "Classical ML algorithms library"},
        {"skill": "SQL",               "priority": "high",         "category": "Database",    "time_weeks": 4,  "description": "Data querying and manipulation"},
        {"skill": "Statistics",        "priority": "high",         "category": "Core Concept","time_weeks": 8,  "description": "Probability, distributions, inference"},
        {"skill": "Data Analysis",     "priority": "high",         "category": "Core Concept","time_weeks": 6,  "description": "EDA and feature engineering"},
        {"skill": "NLP",               "priority": "medium",       "category": "Specialization","time_weeks": 8,"description": "Text processing and language models"},
        {"skill": "LLM",               "priority": "medium",       "category": "Specialization","time_weeks": 6,"description": "Large language models and fine-tuning"},
        {"skill": "LangChain",         "priority": "medium",       "category": "Framework",   "time_weeks": 3,  "description": "LLM application development"},
        {"skill": "Git",               "priority": "medium",       "category": "Tool",        "time_weeks": 2,  "description": "Version control"},
        {"skill": "Docker",            "priority": "medium",       "category": "Tool",        "time_weeks": 3,  "description": "Containerized ML deployment"},
        {"skill": "FastAPI",           "priority": "low",          "category": "Framework",   "time_weeks": 3,  "description": "ML model serving APIs"},
    ],
    "Data Scientist": [
        {"skill": "Python",            "priority": "critical",     "category": "Language",    "time_weeks": 12},
        {"skill": "Statistics",        "priority": "critical",     "category": "Core Concept","time_weeks": 10},
        {"skill": "Machine Learning",  "priority": "critical",     "category": "Core Concept","time_weeks": 16},
        {"skill": "SQL",               "priority": "critical",     "category": "Database",    "time_weeks": 6},
        {"skill": "Data Analysis",     "priority": "high",         "category": "Core Concept","time_weeks": 8},
        {"skill": "Scikit-Learn",      "priority": "high",         "category": "Library",     "time_weeks": 4},
        {"skill": "Data Visualization","priority": "high",         "category": "Tool",        "time_weeks": 4},
        {"skill": "R",                 "priority": "medium",       "category": "Language",    "time_weeks": 6},
        {"skill": "Pandas",            "priority": "high",         "category": "Library",     "time_weeks": 3},
        {"skill": "NumPy",             "priority": "high",         "category": "Library",     "time_weeks": 2},
        {"skill": "Deep Learning",     "priority": "medium",       "category": "Core Concept","time_weeks": 12},
        {"skill": "Big Data",          "priority": "medium",       "category": "Tool",        "time_weeks": 6},
        {"skill": "Git",               "priority": "medium",       "category": "Tool",        "time_weeks": 2},
    ],
    "Data Analyst": [
        {"skill": "SQL",               "priority": "critical",     "category": "Database",    "time_weeks": 6},
        {"skill": "Excel",             "priority": "critical",     "category": "Tool",        "time_weeks": 3},
        {"skill": "Data Analysis",     "priority": "critical",     "category": "Core Concept","time_weeks": 6},
        {"skill": "Data Visualization","priority": "high",         "category": "Tool",        "time_weeks": 4},
        {"skill": "Python",            "priority": "high",         "category": "Language",    "time_weeks": 8},
        {"skill": "Tableau",           "priority": "high",         "category": "Tool",        "time_weeks": 4},
        {"skill": "Power BI",          "priority": "high",         "category": "Tool",        "time_weeks": 4},
        {"skill": "Statistics",        "priority": "high",         "category": "Core Concept","time_weeks": 6},
        {"skill": "Communication",     "priority": "high",         "category": "Soft Skill",  "time_weeks": 4},
        {"skill": "Problem-Solving",   "priority": "medium",       "category": "Soft Skill",  "time_weeks": 4},
        {"skill": "Machine Learning",  "priority": "medium",       "category": "Core Concept","time_weeks": 12},
    ],
    "Data Engineer": [
        {"skill": "Python",            "priority": "critical",     "category": "Language",    "time_weeks": 10},
        {"skill": "SQL",               "priority": "critical",     "category": "Database",    "time_weeks": 6},
        {"skill": "PostgreSQL",        "priority": "high",         "category": "Database",    "time_weeks": 4},
        {"skill": "Apache Spark",      "priority": "high",         "category": "Framework",   "time_weeks": 8},
        {"skill": "AWS",               "priority": "high",         "category": "Cloud",       "time_weeks": 8},
        {"skill": "Docker",            "priority": "high",         "category": "Tool",        "time_weeks": 3},
        {"skill": "Git",               "priority": "medium",       "category": "Tool",        "time_weeks": 2},
        {"skill": "Big Data",          "priority": "medium",       "category": "Concept",     "time_weeks": 6},
        {"skill": "REST APIs",         "priority": "medium",       "category": "Concept",     "time_weeks": 4},
        {"skill": "Data Analysis",     "priority": "medium",       "category": "Core Concept","time_weeks": 4},
    ],
    "Full Stack Engineer": [
        {"skill": "React",             "priority": "critical",     "category": "Frontend",    "time_weeks": 8},
        {"skill": "JavaScript",        "priority": "critical",     "category": "Language",    "time_weeks": 10},
        {"skill": "TypeScript",        "priority": "critical",     "category": "Language",    "time_weeks": 4},
        {"skill": "Node.js",           "priority": "critical",     "category": "Backend",     "time_weeks": 6},
        {"skill": "SQL",               "priority": "high",         "category": "Database",    "time_weeks": 4},
        {"skill": "REST APIs",         "priority": "high",         "category": "Concept",     "time_weeks": 4},
        {"skill": "PostgreSQL",        "priority": "high",         "category": "Database",    "time_weeks": 3},
        {"skill": "Git",               "priority": "high",         "category": "Tool",        "time_weeks": 2},
        {"skill": "Docker",            "priority": "medium",       "category": "Tool",        "time_weeks": 3},
        {"skill": "Next.js",           "priority": "medium",       "category": "Frontend",    "time_weeks": 4},
        {"skill": "CSS",               "priority": "medium",       "category": "Frontend",    "time_weeks": 3},
        {"skill": "Python",            "priority": "medium",       "category": "Language",    "time_weeks": 6},
    ],
    "Frontend Developer": [
        {"skill": "React",             "priority": "critical",     "category": "Framework",   "time_weeks": 8},
        {"skill": "JavaScript",        "priority": "critical",     "category": "Language",    "time_weeks": 10},
        {"skill": "TypeScript",        "priority": "critical",     "category": "Language",    "time_weeks": 4},
        {"skill": "HTML",              "priority": "critical",     "category": "Language",    "time_weeks": 3},
        {"skill": "CSS",               "priority": "critical",     "category": "Language",    "time_weeks": 4},
        {"skill": "Tailwind CSS",      "priority": "high",         "category": "Framework",   "time_weeks": 2},
        {"skill": "Next.js",           "priority": "high",         "category": "Framework",   "time_weeks": 4},
        {"skill": "Git",               "priority": "high",         "category": "Tool",        "time_weeks": 2},
        {"skill": "REST APIs",         "priority": "medium",       "category": "Concept",     "time_weeks": 3},
        {"skill": "Testing",           "priority": "medium",       "category": "Practice",    "time_weeks": 3},
    ],
    "Backend Engineer": [
        {"skill": "Python",            "priority": "critical",     "category": "Language",    "time_weeks": 10},
        {"skill": "Node.js",           "priority": "high",         "category": "Language",    "time_weeks": 6},
        {"skill": "SQL",               "priority": "critical",     "category": "Database",    "time_weeks": 6},
        {"skill": "REST APIs",         "priority": "critical",     "category": "Concept",     "time_weeks": 4},
        {"skill": "PostgreSQL",        "priority": "high",         "category": "Database",    "time_weeks": 3},
        {"skill": "Docker",            "priority": "high",         "category": "Tool",        "time_weeks": 3},
        {"skill": "Microservices",     "priority": "high",         "category": "Architecture","time_weeks": 6},
        {"skill": "Redis",             "priority": "medium",       "category": "Database",    "time_weeks": 2},
        {"skill": "Git",               "priority": "high",         "category": "Tool",        "time_weeks": 2},
        {"skill": "FastAPI",           "priority": "medium",       "category": "Framework",   "time_weeks": 3},
        {"skill": "Django",            "priority": "medium",       "category": "Framework",   "time_weeks": 4},
    ],
    "Software Developer": [
        {"skill": "Python",            "priority": "critical",     "category": "Language",    "time_weeks": 10},
        {"skill": "JavaScript",        "priority": "high",         "category": "Language",    "time_weeks": 8},
        {"skill": "Data Structures & Algorithms", "priority": "critical", "category": "Core Concept", "time_weeks": 12},
        {"skill": "Object-Oriented Programming",  "priority": "critical", "category": "Core Concept", "time_weeks": 6},
        {"skill": "SQL",               "priority": "high",         "category": "Database",    "time_weeks": 4},
        {"skill": "Git",               "priority": "high",         "category": "Tool",        "time_weeks": 2},
        {"skill": "REST APIs",         "priority": "high",         "category": "Concept",     "time_weeks": 4},
        {"skill": "Testing",           "priority": "medium",       "category": "Practice",    "time_weeks": 4},
        {"skill": "Software Design Patterns", "priority": "medium","category": "Concept",     "time_weeks": 6},
    ],
    "DevOps & Cloud Engineer": [
        {"skill": "Docker",            "priority": "critical",     "category": "Tool",        "time_weeks": 4},
        {"skill": "Kubernetes",        "priority": "critical",     "category": "Tool",        "time_weeks": 6},
        {"skill": "AWS",               "priority": "critical",     "category": "Cloud",       "time_weeks": 10},
        {"skill": "CI/CD",             "priority": "critical",     "category": "Practice",    "time_weeks": 4},
        {"skill": "Linux",             "priority": "critical",     "category": "OS",          "time_weeks": 6},
        {"skill": "Python",            "priority": "high",         "category": "Language",    "time_weeks": 6},
        {"skill": "Terraform",         "priority": "high",         "category": "Tool",        "time_weeks": 4},
        {"skill": "Git",               "priority": "high",         "category": "Tool",        "time_weeks": 2},
        {"skill": "GCP",               "priority": "medium",       "category": "Cloud",       "time_weeks": 6},
        {"skill": "Azure",             "priority": "medium",       "category": "Cloud",       "time_weeks": 6},
        {"skill": "Monitoring",        "priority": "medium",       "category": "Practice",    "time_weeks": 3},
    ],
    "Cybersecurity Analyst": [
        {"skill": "Network Security",  "priority": "critical",     "category": "Core",        "time_weeks": 12},
        {"skill": "Ethical Hacking",   "priority": "critical",     "category": "Core",        "time_weeks": 10},
        {"skill": "Linux",             "priority": "critical",     "category": "OS",          "time_weeks": 6},
        {"skill": "Python",            "priority": "high",         "category": "Language",    "time_weeks": 8},
        {"skill": "Cryptography",      "priority": "high",         "category": "Core",        "time_weeks": 6},
        {"skill": "Penetration Testing","priority": "high",        "category": "Skill",       "time_weeks": 8},
        {"skill": "SIEM Tools",        "priority": "high",         "category": "Tool",        "time_weeks": 4},
        {"skill": "Incident Response", "priority": "high",         "category": "Process",     "time_weeks": 4},
        {"skill": "Firewall Management","priority": "medium",      "category": "Tool",        "time_weeks": 3},
        {"skill": "SQL",               "priority": "medium",       "category": "Database",    "time_weeks": 3},
        {"skill": "Git",               "priority": "low",          "category": "Tool",        "time_weeks": 2},
    ],
    "Mobile App Developer": [
        {"skill": "React Native",      "priority": "critical",     "category": "Framework",   "time_weeks": 8},
        {"skill": "Flutter",           "priority": "critical",     "category": "Framework",   "time_weeks": 8},
        {"skill": "JavaScript",        "priority": "high",         "category": "Language",    "time_weeks": 8},
        {"skill": "TypeScript",        "priority": "high",         "category": "Language",    "time_weeks": 4},
        {"skill": "Android / Kotlin",  "priority": "high",         "category": "Platform",    "time_weeks": 10},
        {"skill": "iOS / Swift",       "priority": "high",         "category": "Platform",    "time_weeks": 10},
        {"skill": "REST APIs",         "priority": "high",         "category": "Concept",     "time_weeks": 3},
        {"skill": "Git",               "priority": "medium",       "category": "Tool",        "time_weeks": 2},
        {"skill": "Firebase",          "priority": "medium",       "category": "Backend",     "time_weeks": 3},
        {"skill": "UI/UX Design",      "priority": "medium",       "category": "Design",      "time_weeks": 4},
    ],
}

PRIORITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def get_enhanced_skill_gap(
    student_skills: List[Any],
    career_title: str,
) -> Dict[str, Any]:
    """
    Compute a detailed, priority-ranked skill gap analysis for a target career.
    Uses the authoritative CAREER_SKILL_REQUIREMENTS mapping (deterministic, not ML).

    Returns:
      {
        target_career, analysis_method, matching_skills, missing_skills (priority-sorted),
        skill_categories, completion_percentage, estimated_weeks_to_ready,
        possessed_skills_detail, learning_path_summary
      }
    """
    # Normalize student skills to lowercase set
    student_skill_names: set = set()
    for s in student_skills:
        if isinstance(s, str):
            student_skill_names.add(s.strip().lower())
        elif isinstance(s, dict):
            name = s.get("name") or s.get("skill") or ""
            if name:
                student_skill_names.add(name.strip().lower())

    # Find career requirements — try exact match, then partial
    requirements = None
    career_lower = career_title.strip().lower()
    for key in CAREER_SKILL_REQUIREMENTS:
        if key.lower() == career_lower:
            requirements = CAREER_SKILL_REQUIREMENTS[key]
            career_title = key
            break
    if requirements is None:
        for key in CAREER_SKILL_REQUIREMENTS:
            if career_lower in key.lower() or key.lower() in career_lower:
                requirements = CAREER_SKILL_REQUIREMENTS[key]
                career_title = key
                break

    if requirements is None:
        # Generic fallback
        return {
            "target_career":        career_title,
            "analysis_method":      "rule_based_career_mapping",
            "analysis_label":       "Rule-Based Career Mapping",
            "error":                f"No detailed skill map available for '{career_title}'. Using basic comparison.",
            "matching_skills":      [],
            "missing_skills":       [],
            "completion_percentage": 0.0,
        }

    matching_skills: List[str] = []
    missing_skills: List[Dict[str, Any]] = []
    total_weeks_needed = 0

    for req in requirements:
        skill = req["skill"]
        skill_lower = skill.lower()
        priority = req.get("priority", "medium")
        category = req.get("category", "General")
        time_weeks = req.get("time_weeks", 4)
        desc = req.get("description", "")

        # Check if student has this skill (fuzzy)
        is_possessed = (
            skill_lower in student_skill_names
            or any(skill_lower in sn or sn in skill_lower for sn in student_skill_names if len(sn) > 2)
        )

        if is_possessed:
            matching_skills.append(skill)
        else:
            missing_skills.append({
                "skill":      skill,
                "priority":   priority,
                "category":   category,
                "time_weeks": time_weeks,
                "description": desc,
                "status":     "missing",
                "importance": priority,  # backward compat with existing API
            })
            if priority in ("critical", "high"):
                total_weeks_needed += time_weeks

    # Sort missing skills by priority order
    missing_skills.sort(key=lambda x: PRIORITY_ORDER.get(x["priority"], 99))

    # Categorize missing skills
    skill_categories: Dict[str, List[str]] = {}
    for item in missing_skills:
        cat = item["category"]
        skill_categories.setdefault(cat, []).append(item["skill"])

    total_req = len(requirements)
    total_matching = len(matching_skills)
    completion_pct = round(total_matching / total_req * 100, 1) if total_req else 0.0

    # Priority breakdown
    critical_missing = [s for s in missing_skills if s["priority"] == "critical"]
    high_missing     = [s for s in missing_skills if s["priority"] == "high"]
    medium_missing   = [s for s in missing_skills if s["priority"] == "medium"]
    low_missing      = [s for s in missing_skills if s["priority"] == "low"]

    # Learning path summary
    if not critical_missing and not high_missing:
        readiness_status = "advanced"
        readiness_label  = "Ready to Apply"
        readiness_note   = "You have all critical and high-priority skills. Polish your portfolio and practice interviews."
    elif not critical_missing:
        readiness_status = "intermediate"
        readiness_label  = "Nearly Ready"
        readiness_note   = f"Focus on {len(high_missing)} high-priority skill(s) to strengthen your profile."
    else:
        readiness_status = "developing"
        readiness_label  = "Building Foundation"
        readiness_note   = f"Address {len(critical_missing)} critical skill(s) first: {', '.join(s['skill'] for s in critical_missing[:3])}."

    return {
        "target_career":            career_title,
        "analysis_method":          "rule_based_career_mapping",
        "analysis_label":           "Rule-Based Career Mapping",
        "matching_skills":          matching_skills,
        "missing_skills":           missing_skills,
        "completion_percentage":    completion_pct,
        "total_required":           total_req,
        "total_matching":           total_matching,
        "skill_categories":         skill_categories,
        "priority_breakdown": {
            "critical": len(critical_missing),
            "high":     len(high_missing),
            "medium":   len(medium_missing),
            "low":      len(low_missing),
        },
        "estimated_weeks_for_critical_high": total_weeks_needed,
        "readiness_status": readiness_status,
        "readiness_label":  readiness_label,
        "readiness_note":   readiness_note,
    }


def get_available_career_titles() -> List[str]:
    """Return all career titles with a defined skill requirement map."""
    return list(CAREER_SKILL_REQUIREMENTS.keys())
