"""
ML Data Builder — Training Data Pipeline
Loads students_database.json and builds clean, split-safe DataFrames
for all ML models. Handles train/test splitting with no data leakage.
"""
import os
import json
import logging
from typing import Tuple, Dict, Any, List
import pandas as pd
from sklearn.model_selection import train_test_split

from app.core.config import settings
from app.ml.preprocessor import build_feature_dataframe

logger = logging.getLogger(__name__)

DATA_DIR = settings.DATA_DIR
TEST_SIZE = 0.20
RANDOM_STATE = 42

# Career label normalization map — maps raw labels from students_database
# to canonical career titles used throughout CareerPilot AI
CAREER_LABEL_MAP: Dict[str, str] = {
    "ai/ml engineer":               "AI / Machine Learning Engineer",
    "machine learning engineer":    "AI / Machine Learning Engineer",
    "ml engineer":                  "AI / Machine Learning Engineer",
    "artificial intelligence":      "AI / Machine Learning Engineer",
    "data scientist":               "Data Scientist",
    "data science":                 "Data Scientist",
    "data analyst":                 "Data Analyst",
    "data analytics":               "Data Analyst",
    "business analyst":             "Data Analyst",
    "data engineer":                "Data Engineer",
    "software developer":           "Software Developer",
    "software engineer":            "Software Developer",
    "full stack":                   "Full Stack Engineer",
    "full stack engineer":          "Full Stack Engineer",
    "full stack developer":         "Full Stack Engineer",
    "frontend developer":           "Frontend Developer",
    "front end developer":          "Frontend Developer",
    "ui developer":                 "Frontend Developer",
    "backend developer":            "Backend Engineer",
    "backend engineer":             "Backend Engineer",
    "server side developer":        "Backend Engineer",
    "devops engineer":              "DevOps & Cloud Engineer",
    "cloud engineer":               "DevOps & Cloud Engineer",
    "devops":                       "DevOps & Cloud Engineer",
    "cloud developer":              "DevOps & Cloud Engineer",
    "cybersecurity analyst":        "Cybersecurity Analyst",
    "security analyst":             "Cybersecurity Analyst",
    "cybersecurity":                "Cybersecurity Analyst",
    "information security":         "Cybersecurity Analyst",
    "mobile app developer":         "Mobile App Developer",
    "mobile developer":             "Mobile App Developer",
    "android developer":            "Mobile App Developer",
    "ios developer":                "Mobile App Developer",
    "web developer":                "Full Stack Engineer",
}

# Minimum samples per career class for RF classification training
MIN_SAMPLES_PER_CLASS = 5


def _normalize_career_label(raw: str) -> str:
    """Map raw career string to canonical CareerPilot AI career title."""
    norm = raw.strip().lower()
    if norm in CAREER_LABEL_MAP:
        return CAREER_LABEL_MAP[norm]
    # Partial match
    for key, val in CAREER_LABEL_MAP.items():
        if key in norm or norm in key:
            return val
    # Title-case the original as fallback (preserves unseen careers)
    return raw.strip().title()


def load_students_database() -> List[Dict[str, Any]]:
    """Load students_database.json (or CSV fallback) from data directory."""
    json_path = os.path.join(DATA_DIR, "students_database.json")
    csv_path  = os.path.join(DATA_DIR, "students_database.csv")

    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            records = json.load(f)
        logger.info(f"Loaded {len(records)} student records from students_database.json")
        return records

    if os.path.exists(csv_path):
        import csv
        rows = []
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Parse list-like fields from comma-separated strings
                for field in ("technical_skills", "soft_skills"):
                    if isinstance(row.get(field), str):
                        row[field] = [s.strip() for s in row[field].split(",") if s.strip()]
                rows.append(dict(row))
        logger.info(f"Loaded {len(rows)} student records from students_database.csv")
        return rows

    logger.warning("No students_database found — returning empty list")
    return []


def prepare_training_data() -> Tuple[
    pd.DataFrame, pd.DataFrame,  # X_train, X_test
    pd.Series, pd.Series,        # y_readiness_train, y_readiness_test
    pd.Series, pd.Series,        # y_career_train, y_career_test
]:
    """
    Load and split training data for all ML models.
    Applies stratified split by career label.
    Returns 6-tuple: X_train, X_test, y_read_train, y_read_test, y_car_train, y_car_test
    """
    records = load_students_database()
    if not records:
        raise ValueError("No student training data available. Upload students_database.json to backend/data/")

    # Normalize career labels before building features
    normalized_records = []
    for rec in records:
        career_raw = rec.get("target_career", "")
        rec = dict(rec)
        rec["target_career"] = _normalize_career_label(career_raw)
        normalized_records.append(rec)

    X, y_readiness, y_career = build_feature_dataframe(normalized_records)

    if X.empty:
        raise ValueError("Feature extraction produced empty DataFrame — check data format")

    # Filter out career classes with too few samples for stratification
    career_counts = y_career.value_counts()
    valid_careers = career_counts[career_counts >= MIN_SAMPLES_PER_CLASS].index.tolist()
    mask = y_career.isin(valid_careers)

    if mask.sum() < 10:
        raise ValueError(
            f"Insufficient training data after filtering: {mask.sum()} samples across "
            f"{len(valid_careers)} career classes. Need at least 10 samples."
        )

    X_filtered = X[mask].reset_index(drop=True)
    y_readiness_filtered = y_readiness[mask].reset_index(drop=True)
    y_career_filtered = y_career[mask].reset_index(drop=True)

    logger.info(
        f"Training data: {X_filtered.shape[0]} samples, {X_filtered.shape[1]} features, "
        f"{y_career_filtered.nunique()} career classes"
    )

    # Stratified split by career label
    X_train, X_test, y_read_train, y_read_test, y_car_train, y_car_test = train_test_split(
        X_filtered, y_readiness_filtered, y_career_filtered,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y_career_filtered,
    )

    logger.info(f"Split: train={len(X_train)}, test={len(X_test)}")
    return X_train, X_test, y_read_train, y_read_test, y_car_train, y_car_test


def get_all_career_labels(records: List[Dict[str, Any]] = None) -> List[str]:
    """Return sorted list of all canonical career labels in the training data."""
    if records is None:
        records = load_students_database()
    labels = set()
    for rec in records:
        label = _normalize_career_label(rec.get("target_career", ""))
        if label:
            labels.add(label)
    return sorted(labels)
