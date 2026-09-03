"""
ML Model Registry — Singleton Manager for All CareerPilot AI ML Models
Provides thread-safe lazy loading, training coordination,
and status reporting for all ML models.
"""
import threading
import logging
from typing import Optional, Dict, Any

from app.ml.readiness_model import ReadinessModel
from app.ml.career_model    import CareerModel

logger = logging.getLogger(__name__)

_lock = threading.Lock()

# ── Singleton instances ────────────────────────────────────────────────────────
_readiness_model: Optional[ReadinessModel] = None
_career_model:    Optional[CareerModel]    = None

_models_loaded = False


def _ensure_loaded():
    """Lazy-load all models from disk on first access."""
    global _readiness_model, _career_model, _models_loaded

    if _models_loaded:
        return

    with _lock:
        if _models_loaded:
            return

        logger.info("ML Model Registry: loading persisted models from disk...")

        _readiness_model = ReadinessModel()
        _career_model    = CareerModel()

        r_loaded = _readiness_model.load()
        c_loaded = _career_model.load()

        logger.info(
            f"ML Registry loaded — "
            f"Readiness(RF)={'✓' if r_loaded else '✗ (not trained)'} | "
            f"Career(RF)={'✓' if c_loaded else '✗ (not trained)'}"
        )
        _models_loaded = True


def get_readiness_model() -> ReadinessModel:
    _ensure_loaded()
    return _readiness_model


def get_career_model() -> CareerModel:
    _ensure_loaded()
    return _career_model


def train_all_models() -> Dict[str, Any]:
    """
    Train all ML models using the students_database dataset.
    Returns a comprehensive training report.
    Raises ValueError if training data is insufficient.
    """
    global _readiness_model, _career_model, _models_loaded

    from app.ml.data_builder import prepare_training_data

    logger.info("ML Registry: starting full model training...")

    # Build training data
    X_train, X_test, y_read_train, y_read_test, y_car_train, y_car_test = (
        prepare_training_data()
    )

    report: Dict[str, Any] = {
        "training_samples": int(len(X_train)),
        "test_samples":     int(len(X_test)),
        "n_career_classes": int(y_car_train.nunique()),
        "models":           {},
    }

    errors: Dict[str, str] = {}

    # 1. Train Readiness RF
    with _lock:
        try:
            model = ReadinessModel()
            metrics = model.train(X_train, y_read_train, X_test, y_read_test)
            model.save()
            _readiness_model = model
            report["models"]["readiness_rf"] = {
                "status":  "trained",
                "metrics": metrics,
                "method":  model.PREDICTION_METHOD,
            }
            logger.info(f"Readiness RF trained and saved — metrics: {metrics}")
        except Exception as e:
            logger.error(f"Readiness RF training failed: {e}", exc_info=True)
            errors["readiness_rf"] = str(e)
            report["models"]["readiness_rf"] = {"status": "failed", "error": str(e)}

    # 2. Train Career RF
    with _lock:
        try:
            model = CareerModel()
            metrics = model.train(X_train, y_car_train, X_test, y_car_test)
            model.save()
            _career_model = model
            report["models"]["career_rf"] = {
                "status":  "trained",
                "metrics": metrics,
                "method":  model.PREDICTION_METHOD,
                "classes": model.get_class_labels(),
            }
            logger.info(f"Career RF trained and saved — metrics: {metrics}")
        except Exception as e:
            logger.error(f"Career RF training failed: {e}", exc_info=True)
            errors["career_rf"] = str(e)
            report["models"]["career_rf"] = {"status": "failed", "error": str(e)}

    _models_loaded = True
    report["success"] = len(errors) == 0
    report["errors"]  = errors

    logger.info(f"ML training complete — success={report['success']}, errors={list(errors.keys())}")
    return report


def get_registry_status() -> Dict[str, Any]:
    """Return current status of all ML models including metrics."""
    _ensure_loaded()

    def model_status(model, name: str) -> Dict[str, Any]:
        if model is None or not model.is_trained:
            return {"status": "not_trained", "name": name}
        meta = model.get_metadata()
        return {
            "status":          "trained",
            "name":            name,
            "trained_at":      meta.get("trained_at", "unknown"),
            "train_samples":   meta.get("train_samples"),
            "metrics":         meta.get("metrics", {}),
            "prediction_method": meta.get("prediction_method", "unknown"),
        }

    return {
        "readiness_rf": model_status(_readiness_model, "Random Forest Regression (Readiness)"),
        "career_rf":    model_status(_career_model,    "Random Forest Classifier (Career)"),
    }


def reset_registry():
    """Force reload of all models (used after training)."""
    global _models_loaded
    with _lock:
        _models_loaded = False
