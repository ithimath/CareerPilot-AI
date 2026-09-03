"""
ML Preprocessor — Shared Feature Engineering Utilities
Converts raw student profile records (both training format and live Firestore format)
into a consistent numerical feature matrix usable by all ML models.
"""
import logging
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

# ── Canonical Skill Vocabulary (Multi-hot encoding) ───────────────────────────
# Top skills extracted from students_database.json — used for multi-hot features
SKILL_VOCAB = [
    "python", "javascript", "java", "c++", "c", "r", "go", "swift", "kotlin",
    "typescript", "sql", "html", "css", "bash", "matlab",
    "react", "node.js", "angular", "vue", "django", "flask", "fastapi",
    "spring", "express", "next.js", "flutter", "react native",
    "tensorflow", "pytorch", "scikit-learn", "keras",
    "machine learning", "deep learning", "nlp", "computer vision", "data analysis",
    "data science", "statistics", "big data", "spark",
    "aws", "azure", "gcp", "docker", "kubernetes", "ci/cd", "terraform",
    "linux", "git", "devops", "ansible",
    "postgresql", "mysql", "mongodb", "redis", "sqlite", "firebase",
    "network security", "ethical hacking", "cryptography", "penetration testing",
    "excel", "tableau", "power bi", "data visualization",
    "project management", "business strategy", "communication", "leadership",
    "problem-solving", "agile", "rest apis", "microservices",
]

SKILL_VOCAB_SET = set(SKILL_VOCAB)
SKILL_VOCAB_INDEX = {skill: idx for idx, skill in enumerate(SKILL_VOCAB)}

# ── Academic Year Encoding ─────────────────────────────────────────────────────
ACADEMIC_YEAR_MAP = {
    "1st year": 1,
    "1st": 1,
    "2nd year": 2,
    "2nd": 2,
    "3rd year": 3,
    "3rd": 3,
    "final year": 4,
    "final": 4,
    "4th year": 4,
    "4th": 4,
    "postgrad": 5,
    "phd": 6,
}

# ── Course Category Encoding ───────────────────────────────────────────────────
def _course_to_category(course: str) -> Dict[str, int]:
    """Return one-hot category flags for a course name."""
    c = (course or "").lower()
    return {
        "is_cs_course":     int(any(x in c for x in ["computer science", "b.tech cs", "be cs", "cse", "b.tech it", "information technology"])),
        "is_data_course":   int(any(x in c for x in ["data science", "data analytics", "b.sc data", "m.sc data"])),
        "is_ai_course":     int(any(x in c for x in ["artificial intelligence", "m.tech ai", "b.tech ai"])),
        "is_business_course": int(any(x in c for x in ["mba", "bba", "business", "management"])),
        "is_engineering":   int(any(x in c for x in ["b.tech", "be ", "m.tech", "b.e."])),
        "is_science":       int(any(x in c for x in ["b.sc", "m.sc", "b.s.", "m.s."])),
    }


def _normalize_skill(skill: str) -> str:
    """Lowercase + strip a skill name."""
    return (skill or "").strip().lower()


def _skills_to_multihot(skills: List[str]) -> np.ndarray:
    """Convert a list of skill names to a multi-hot binary vector."""
    vec = np.zeros(len(SKILL_VOCAB), dtype=np.float32)
    for skill in skills:
        norm = _normalize_skill(skill)
        if norm in SKILL_VOCAB_INDEX:
            vec[SKILL_VOCAB_INDEX[norm]] = 1.0
        # Partial match for longer skill names
        else:
            for vocab_skill in SKILL_VOCAB:
                if vocab_skill in norm or norm in vocab_skill:
                    vec[SKILL_VOCAB_INDEX[vocab_skill]] = 1.0
                    break
    return vec


# ── Feature Column Names (for interpretability / feature importance) ───────────
def get_feature_names() -> List[str]:
    """Return ordered list of all feature column names."""
    cols = []
    # Aggregate features
    cols += [
        "num_technical_skills",
        "num_soft_skills",
        "has_projects",
        "academic_year_num",
        "cgpa_normalized",
        "num_certifications",
        "num_internships",
    ]
    # Course category
    cols += [
        "is_cs_course", "is_data_course", "is_ai_course",
        "is_business_course", "is_engineering", "is_science",
    ]
    # Multi-hot skill features
    cols += [f"skill_{s.replace(' ', '_').replace('/', '_').replace('.', '_')}" for s in SKILL_VOCAB]
    return cols


FEATURE_NAMES = get_feature_names()
N_FEATURES = len(FEATURE_NAMES)


# ── Main Extraction Functions ─────────────────────────────────────────────────

def extract_features_from_training_record(record: Dict[str, Any]) -> Optional[np.ndarray]:
    """
    Extract features from a students_database.json record.
    Format: {technical_skills, soft_skills, academic_year, enrolled_course,
              projects_completed, readiness_rating, target_career}
    Returns None if record is missing critical fields.
    """
    try:
        tech_skills = record.get("technical_skills") or []
        soft_skills = record.get("soft_skills") or []
        academic_year_raw = (record.get("academic_year") or "").lower()
        course_raw = record.get("enrolled_course") or ""
        projects_done = 1.0 if str(record.get("projects_completed", "")).lower() == "yes" else 0.0

        # Aggregate numeric features
        num_tech = float(len(tech_skills))
        num_soft = float(len(soft_skills))
        year_num = float(ACADEMIC_YEAR_MAP.get(academic_year_raw, 2))  # default 2nd year
        cgpa_norm = float(min(record.get("cgpa", 7.0) or 7.0, 10.0)) / 10.0
        num_certs = float(record.get("num_certifications", 0) or 0)
        num_interns = float(record.get("num_internships", 0) or 0)

        aggregates = np.array([
            num_tech, num_soft, projects_done, year_num,
            cgpa_norm, num_certs, num_interns,
        ], dtype=np.float32)

        # Course category
        course_cats = _course_to_category(course_raw)
        course_vec = np.array(list(course_cats.values()), dtype=np.float32)

        # Skill multi-hot (combine tech + soft)
        all_skills = list(tech_skills) + list(soft_skills)
        skill_vec = _skills_to_multihot(all_skills)

        return np.concatenate([aggregates, course_vec, skill_vec])
    except Exception as e:
        logger.warning(f"Feature extraction failed for training record: {e}")
        return None


def extract_features_from_live_profile(profile: Dict[str, Any]) -> np.ndarray:
    """
    Extract features from a live Firestore student profile.
    Format: {skills (list of str/dict), projects, internships, certifications,
              cgpa, interests, target_career, ...}
    Returns zero-padded feature vector if profile is sparse.
    """
    try:
        # Parse skills from flexible format
        raw_skills = profile.get("skills") or []
        parsed_skills = []
        for s in raw_skills:
            if isinstance(s, str):
                parsed_skills.append(s)
            elif isinstance(s, dict):
                name = s.get("name") or s.get("skill") or ""
                if name:
                    parsed_skills.append(name)

        # Also include interests as soft signal
        interests = profile.get("interests") or []
        all_skills = parsed_skills + list(interests)

        projects = profile.get("projects") or []
        internships = profile.get("internships") or []
        certs = profile.get("certifications") or []

        num_tech = float(len(parsed_skills))
        num_soft = float(len([s for s in all_skills if _normalize_skill(s) in {
            "communication", "leadership", "teamwork", "problem-solving",
            "adaptability", "project management", "agile",
        }]))
        has_projects = 1.0 if len(projects) > 0 else 0.0

        # Academic year from profile
        year_raw = str(profile.get("current_year", 2) or 2)
        if year_raw.isdigit():
            year_num = float(min(int(year_raw), 6))
        else:
            year_num = float(ACADEMIC_YEAR_MAP.get(year_raw.lower(), 2))

        cgpa = float(profile.get("cgpa", 0) or 0)
        cgpa_norm = min(cgpa, 10.0) / 10.0

        num_certs = float(len(certs))
        num_interns = float(len(internships))

        aggregates = np.array([
            num_tech, num_soft, has_projects, year_num,
            cgpa_norm, num_certs, num_interns,
        ], dtype=np.float32)

        # Course category from degree field
        degree = profile.get("degree") or profile.get("enrolled_course") or ""
        course_cats = _course_to_category(degree)
        course_vec = np.array(list(course_cats.values()), dtype=np.float32)

        # Skill multi-hot
        skill_vec = _skills_to_multihot(all_skills)

        return np.concatenate([aggregates, course_vec, skill_vec])

    except Exception as e:
        logger.warning(f"Feature extraction failed for live profile: {e}")
        return np.zeros(N_FEATURES, dtype=np.float32)


def build_feature_dataframe(records: List[Dict[str, Any]], source: str = "training") -> Tuple[pd.DataFrame, pd.Series, pd.Series]:
    """
    Build a full feature DataFrame from a list of training records.
    Returns (X_df, y_readiness, y_career) where:
      - y_readiness: readiness_rating × 20 (0–100 regression target)
      - y_career: target_career string (classification target)
    """
    X_rows = []
    y_readiness_vals = []
    y_career_vals = []

    for rec in records:
        feats = extract_features_from_training_record(rec)
        if feats is None:
            continue

        readiness_score = float((rec.get("readiness_rating") or 3)) * 20.0
        career = str(rec.get("target_career") or "").strip()

        if not career:
            continue

        X_rows.append(feats)
        y_readiness_vals.append(readiness_score)
        y_career_vals.append(career)

    if not X_rows:
        return pd.DataFrame(), pd.Series(dtype=float), pd.Series(dtype=str)

    X = pd.DataFrame(X_rows, columns=FEATURE_NAMES)
    y_readiness = pd.Series(y_readiness_vals, name="readiness_score", dtype=float)
    y_career = pd.Series(y_career_vals, name="target_career", dtype=str)

    logger.info(f"Built feature DataFrame: {X.shape[0]} samples, {X.shape[1]} features")
    return X, y_readiness, y_career
