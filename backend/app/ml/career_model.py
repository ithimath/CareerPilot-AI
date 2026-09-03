"""
Random Forest Classification — Career Recommendation Model
Predicts the top-N most suitable career paths for a student profile.
Trained on students_database.json using target_career as label.
Falls back gracefully to rule-based career_service if not trained.
"""
import os
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, classification_report,
)
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline

from app.ml.preprocessor import extract_features_from_live_profile, FEATURE_NAMES

logger = logging.getLogger(__name__)

# ── Paths ─────────────────────────────────────────────────────────────────────
_BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODELS_DIR   = os.path.join(_BACKEND_DIR, "models")
MODEL_PATH   = os.path.join(MODELS_DIR, "career_rf.joblib")
ENC_PATH     = os.path.join(MODELS_DIR, "career_label_encoder.joblib")
META_PATH    = os.path.join(MODELS_DIR, "career_metadata.json")

# ── Career-level explanations (hard-coded for interpretability) ───────────────
CAREER_WHY_TEMPLATES: Dict[str, str] = {
    "AI / Machine Learning Engineer":
        "Your ML/AI skills and Python expertise strongly match this career's core requirements.",
    "Data Scientist":
        "Your statistical and Python skills align with data science workflows.",
    "Data Analyst":
        "Your data analysis tools and SQL skills are foundational for this role.",
    "Data Engineer":
        "Your database and pipeline skills map to data engineering requirements.",
    "Software Developer":
        "Your programming breadth and project experience fit software development.",
    "Full Stack Engineer":
        "Your combination of frontend and backend skills suits full-stack roles.",
    "Frontend Developer":
        "Your JavaScript/React/CSS proficiency aligns with frontend specialization.",
    "Backend Engineer":
        "Your server-side and database skills match backend engineering needs.",
    "DevOps & Cloud Engineer":
        "Your cloud and infrastructure skills are core to DevOps roles.",
    "Cybersecurity Analyst":
        "Your security and networking knowledge fits cybersecurity analyst roles.",
    "Mobile App Developer":
        "Your mobile framework and platform skills match app development.",
}


class CareerModel:
    """
    Random Forest Classification model for career recommendation.
    Prediction method label: "Random Forest Classification"
    """

    PREDICTION_METHOD = "random_forest_classification"

    def __init__(self):
        self._pipeline: Optional[Pipeline] = None
        self._label_encoder: Optional[LabelEncoder] = None
        self._metadata: Dict[str, Any] = {}
        self._class_labels: List[str] = []
        os.makedirs(MODELS_DIR, exist_ok=True)

    @property
    def is_trained(self) -> bool:
        return self._pipeline is not None and self._label_encoder is not None

    def train(self, X_train, y_train, X_test, y_test) -> Dict[str, Any]:
        """
        Train the Random Forest Classifier.
        Returns training metrics dict.
        """
        logger.info(f"Training CareerModel on {len(X_train)} samples, {y_train.nunique()} classes...")

        # Encode string labels to integers
        le = LabelEncoder()
        y_train_enc = le.fit_transform(y_train)
        y_test_enc  = le.transform(y_test)

        self._label_encoder = le
        self._class_labels  = list(le.classes_)

        pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("rf", RandomForestClassifier(
                n_estimators=300,
                max_depth=15,
                min_samples_split=3,
                min_samples_leaf=1,
                max_features="sqrt",
                class_weight="balanced",   # handle class imbalance
                random_state=42,
                n_jobs=-1,
            )),
        ])

        pipeline.fit(X_train, y_train_enc)
        self._pipeline = pipeline

        # Evaluate
        y_pred = pipeline.predict(X_test)
        acc  = float(accuracy_score(y_test_enc, y_pred))
        prec = float(precision_score(y_test_enc, y_pred, average="weighted", zero_division=0))
        rec  = float(recall_score(y_test_enc, y_pred, average="weighted", zero_division=0))
        f1   = float(f1_score(y_test_enc, y_pred, average="weighted", zero_division=0))

        # Per-class F1 for interpretability
        report = classification_report(
            y_test_enc, y_pred,
            target_names=self._class_labels,
            output_dict=True,
            zero_division=0,
        )
        per_class_f1 = {
            cls: round(report[cls]["f1-score"], 4)
            for cls in self._class_labels
            if cls in report
        }

        self._metadata = {
            "model_type":    "RandomForestClassifier",
            "n_estimators":  300,
            "train_samples": int(len(X_train)),
            "test_samples":  int(len(X_test)),
            "n_classes":     len(self._class_labels),
            "class_labels":  self._class_labels,
            "metrics": {
                "accuracy":           round(acc, 4),
                "precision_weighted": round(prec, 4),
                "recall_weighted":    round(rec, 4),
                "f1_weighted":        round(f1, 4),
            },
            "per_class_f1":  per_class_f1,
            "trained_at":    datetime.utcnow().isoformat(),
            "prediction_method": self.PREDICTION_METHOD,
        }

        logger.info(
            f"CareerModel trained — Accuracy={acc:.4f}, F1={f1:.4f}, Classes={len(self._class_labels)}"
        )
        return self._metadata["metrics"]

    def predict_top_n(
        self, profile: Dict[str, Any], top_n: int = 5
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Predict top-N career recommendations with probability scores.
        Returns list of {title, probability_score, reason, prediction_method}
        or None if model not trained.
        """
        if not self.is_trained:
            return None

        try:
            features = extract_features_from_live_profile(profile)
            import pandas as pd
            X = pd.DataFrame(features.reshape(1, -1), columns=FEATURE_NAMES)

            probas = self._pipeline.predict_proba(X)[0]
            top_indices = np.argsort(probas)[::-1][:top_n]

            recommendations = []
            for idx in top_indices:
                if probas[idx] < 0.01:
                    continue
                career_title = self._class_labels[idx]
                prob_pct = round(float(probas[idx]) * 100, 1)

                reason = CAREER_WHY_TEMPLATES.get(
                    career_title,
                    f"Your profile shows a {prob_pct}% alignment with {career_title} requirements."
                )

                recommendations.append({
                    "title":              career_title,
                    "probability_score":  prob_pct,
                    "prediction_method":  self.PREDICTION_METHOD,
                    "prediction_label":   "Random Forest Classification",
                    "reason":             reason,
                })

            return recommendations if recommendations else None

        except Exception as e:
            logger.error(f"CareerModel.predict_top_n() failed: {e}", exc_info=True)
            return None

    def save(self) -> None:
        """Persist pipeline and label encoder to disk."""
        if not self.is_trained:
            raise RuntimeError("Cannot save — model not trained")
        joblib.dump(self._pipeline, MODEL_PATH)
        joblib.dump(self._label_encoder, ENC_PATH)
        with open(META_PATH, "w", encoding="utf-8") as f:
            json.dump(self._metadata, f, indent=2, default=str)
        logger.info(f"CareerModel saved to {MODEL_PATH}")

    def load(self) -> bool:
        """Load persisted model. Returns True if successful."""
        if not os.path.exists(MODEL_PATH) or not os.path.exists(ENC_PATH):
            return False
        try:
            self._pipeline = joblib.load(MODEL_PATH)
            self._label_encoder = joblib.load(ENC_PATH)
            self._class_labels = list(self._label_encoder.classes_)
            if os.path.exists(META_PATH):
                with open(META_PATH, "r", encoding="utf-8") as f:
                    self._metadata = json.load(f)
            logger.info(f"CareerModel loaded — {len(self._class_labels)} classes")
            return True
        except Exception as e:
            logger.error(f"Failed to load CareerModel: {e}")
            self._pipeline = None
            self._label_encoder = None
            return False

    def get_metadata(self) -> Dict[str, Any]:
        return dict(self._metadata)

    def get_class_labels(self) -> List[str]:
        return list(self._class_labels)
