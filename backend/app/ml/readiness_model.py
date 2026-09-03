"""
Random Forest Regression — Job Readiness Score Model
Predicts a student's job readiness score (0–100) using profile features.
Trained on students_database.json using readiness_rating × 20 as proxy label.
Falls back gracefully if model not yet trained.
"""
import os
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

from app.ml.preprocessor import extract_features_from_live_profile, FEATURE_NAMES

logger = logging.getLogger(__name__)

# ── Paths ─────────────────────────────────────────────────────────────────────
_BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODELS_DIR   = os.path.join(_BACKEND_DIR, "models")
MODEL_PATH   = os.path.join(MODELS_DIR, "readiness_rf.joblib")
META_PATH    = os.path.join(MODELS_DIR, "readiness_metadata.json")


class ReadinessModel:
    """
    Random Forest Regression model for job readiness prediction.
    Prediction method label: "Random Forest Regression"
    """

    PREDICTION_METHOD = "random_forest_regression"

    def __init__(self):
        self._pipeline: Optional[Pipeline] = None
        self._metadata: Dict[str, Any] = {}
        self._feature_importances: List[Dict[str, Any]] = []
        os.makedirs(MODELS_DIR, exist_ok=True)

    @property
    def is_trained(self) -> bool:
        return self._pipeline is not None

    def train(self, X_train, y_train, X_test, y_test) -> Dict[str, Any]:
        """
        Train the Random Forest Regressor.
        Returns training metrics dict.
        """
        logger.info(f"Training ReadinessModel on {len(X_train)} samples...")

        pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("rf", RandomForestRegressor(
                n_estimators=200,
                max_depth=12,
                min_samples_split=4,
                min_samples_leaf=2,
                max_features="sqrt",
                random_state=42,
                n_jobs=-1,
            )),
        ])

        pipeline.fit(X_train, y_train)
        self._pipeline = pipeline

        # Evaluate on test set
        y_pred = pipeline.predict(X_test)
        y_pred_clipped = np.clip(y_pred, 0.0, 100.0)

        mae  = float(mean_absolute_error(y_test, y_pred_clipped))
        rmse = float(np.sqrt(mean_squared_error(y_test, y_pred_clipped)))
        r2   = float(r2_score(y_test, y_pred_clipped))

        # Feature importances from the RF component
        rf = pipeline.named_steps["rf"]
        importances = rf.feature_importances_
        self._feature_importances = sorted(
            [
                {"feature": FEATURE_NAMES[i], "importance": round(float(importances[i]), 5)}
                for i in range(len(importances))
            ],
            key=lambda x: x["importance"],
            reverse=True,
        )

        self._metadata = {
            "model_type":   "RandomForestRegressor",
            "n_estimators": 200,
            "train_samples": int(len(X_train)),
            "test_samples":  int(len(X_test)),
            "metrics": {
                "mae":  round(mae, 3),
                "rmse": round(rmse, 3),
                "r2":   round(r2, 4),
            },
            "top_features": self._feature_importances[:10],
            "trained_at":   datetime.utcnow().isoformat(),
            "prediction_method": self.PREDICTION_METHOD,
            "label_note": "Target label = readiness_rating × 20 (1→20 … 5→100)",
        }

        logger.info(
            f"ReadinessModel trained — MAE={mae:.2f}, RMSE={rmse:.2f}, R²={r2:.4f}"
        )
        return self._metadata["metrics"]

    def predict(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict job readiness score from a live student profile.
        Returns dict with score, confidence_range, feature_drivers, prediction_method.
        Returns None if model not trained.
        """
        if not self.is_trained:
            return None

        try:
            features = extract_features_from_live_profile(profile)
            import pandas as pd
            X = pd.DataFrame(features.reshape(1, -1), columns=FEATURE_NAMES)

            # Individual tree predictions for confidence interval
            rf = self._pipeline.named_steps["rf"]
            scaler = self._pipeline.named_steps["scaler"]
            X_scaled = scaler.transform(X)

            tree_preds = np.array([
                tree.predict(X_scaled)[0] for tree in rf.estimators_
            ])
            tree_preds = np.clip(tree_preds, 0.0, 100.0)

            score = float(np.clip(self._pipeline.predict(X)[0], 0.0, 100.0))
            conf_low  = float(np.percentile(tree_preds, 10))
            conf_high = float(np.percentile(tree_preds, 90))

            # Top contributing features for this prediction
            feature_values = features
            importances = rf.feature_importances_
            driver_indices = np.argsort(importances)[::-1][:5]
            drivers = []
            for idx in driver_indices:
                if feature_values[idx] > 0 and importances[idx] > 0.005:
                    readable = FEATURE_NAMES[idx].replace("skill_", "").replace("_", " ").title()
                    drivers.append({
                        "factor": readable,
                        "importance": round(float(importances[idx]), 4),
                        "present": bool(feature_values[idx] > 0),
                    })

            return {
                "score":             round(score, 1),
                "confidence_range":  [round(conf_low, 1), round(conf_high, 1)],
                "feature_drivers":   drivers,
                "prediction_method": self.PREDICTION_METHOD,
                "prediction_label":  "Random Forest Regression",
            }
        except Exception as e:
            logger.error(f"ReadinessModel.predict() failed: {e}", exc_info=True)
            return None

    def save(self) -> None:
        """Persist model and metadata to disk."""
        if not self.is_trained:
            raise RuntimeError("Cannot save — model not trained")
        joblib.dump(self._pipeline, MODEL_PATH)
        with open(META_PATH, "w", encoding="utf-8") as f:
            json.dump(self._metadata, f, indent=2, default=str)
        logger.info(f"ReadinessModel saved to {MODEL_PATH}")

    def load(self) -> bool:
        """Load persisted model. Returns True if successful."""
        if not os.path.exists(MODEL_PATH):
            return False
        try:
            self._pipeline = joblib.load(MODEL_PATH)
            if os.path.exists(META_PATH):
                with open(META_PATH, "r", encoding="utf-8") as f:
                    self._metadata = json.load(f)
            logger.info(f"ReadinessModel loaded from {MODEL_PATH}")
            return True
        except Exception as e:
            logger.error(f"Failed to load ReadinessModel: {e}")
            self._pipeline = None
            return False

    def get_metadata(self) -> Dict[str, Any]:
        return dict(self._metadata)

    def get_feature_importances(self, top_n: int = 15) -> List[Dict[str, Any]]:
        return self._feature_importances[:top_n]
