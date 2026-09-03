"""
ML Engine Router — /api/ml/
Provides endpoints for model training, status, and ML-specific predictions.
These supplement (not replace) the existing /api/job-score, /api/careers, /api/skill-gap endpoints.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from app.core.dependencies import get_current_user
from app.core.firebase import get_firestore
from datetime import datetime
from typing import Optional

router = APIRouter()
logger = logging.getLogger(__name__)


# ── POST /api/ml/train ─────────────────────────────────────────────────────────
@router.post("/train")
async def train_all_models(
    n_clusters: int = Query(5, ge=2, le=20, description="Number of K-Means clusters"),
    user: dict = Depends(get_current_user),
):
    """
    Trigger full ML training pipeline using students_database dataset.
    Trains: Random Forest Regressor (readiness), Random Forest Classifier (career),
    K-Means Clustering (student profiling).
    Models are persisted to backend/models/ for reuse across requests.
    Requires authentication.
    """
    uid = user.get("uid", "")
    logger.info(f"ML training triggered by uid={uid}, n_clusters={n_clusters}")
    try:
        from app.ml.model_registry import train_all_models as _train
        report = _train(n_clusters=n_clusters)

        # Log training event
        try:
            db = get_firestore()
            db.collection("mlTrainingHistory").add({
                "triggered_by": uid,
                "trained_at":   datetime.utcnow().isoformat(),
                "n_clusters":   n_clusters,
                "report":       report,
            })
        except Exception:
            pass  # Non-critical

        return {
            "success":    report["success"],
            "message":    "ML models trained successfully" if report["success"] else "Training completed with some errors",
            "report":     report,
            "trained_at": datetime.utcnow().isoformat(),
            "note":       (
                "Models are now persisted and will be used for all subsequent predictions. "
                "Predictions will be labeled with their method (random_forest / tfidf_semantic / rule_based)."
            ),
        }

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"ML training failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")


# ── GET /api/ml/status ─────────────────────────────────────────────────────────
@router.get("/status")
async def get_ml_status():
    """
    Get current status of all ML models including training metrics and timestamps.
    Public endpoint — no authentication required.
    """
    try:
        from app.ml.model_registry import get_registry_status
        status = get_registry_status()
        return {
            "ml_engine_version":  "2.0",
            "models":             status,
            "timestamp":          datetime.utcnow().isoformat(),
            "architecture": {
                "readiness":  "Random Forest Regression (scikit-learn)",
                "career":     "Random Forest Classification (scikit-learn)",
                "clustering": "K-Means Clustering (scikit-learn)",
                "skill_gap":  "Rule-Based Career Mapping (deterministic)",
                "nlp":        "NLP Normalization Pipeline (pure Python dictionary)",
                "chatbot":    "LLM — Gemini 1.5 Flash (Google AI)",
            },
        }
    except Exception as e:
        logger.error(f"ML status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── GET /api/ml/profile-cluster ───────────────────────────────────────────────
@router.get("/profile-cluster")
async def get_student_cluster(user: dict = Depends(get_current_user)):
    """
    Get K-Means cluster assignment for the current authenticated student.
    Returns a human-readable archetype (e.g. "AI/ML Pioneer", "Data Analytics Expert").
    Returns 503 if the clustering model has not been trained yet.
    """
    try:
        db = get_firestore()
        uid = user["uid"]

        profile_doc = db.collection("profiles").document(uid).get()
        if not profile_doc.exists:
            raise HTTPException(status_code=404, detail="Profile not found")

        profile = profile_doc.to_dict() or {}
        profile["uid"] = uid

        from app.ml.model_registry import get_clustering_model
        model = get_clustering_model()

        if not model.is_trained:
            return {
                "cluster_available": False,
                "message": (
                    "Student profiling model not yet trained. "
                    "An admin needs to call POST /api/ml/train first."
                ),
                "prediction_label": "K-Means Clustering (not trained)",
            }

        result = model.assign_cluster(profile)
        if result is None:
            raise HTTPException(status_code=500, detail="Cluster assignment failed")

        result["cluster_available"] = True
        result["uid"] = uid

        # Cache cluster in Firestore
        try:
            db.collection("studentClusters").document(uid).set({
                **result,
                "updated_at": datetime.utcnow().isoformat(),
            })
        except Exception:
            pass

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile cluster failed for uid={user.get('uid')}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ── GET /api/ml/readiness-rf ──────────────────────────────────────────────────
@router.get("/readiness-rf")
async def get_rf_readiness_score(user: dict = Depends(get_current_user)):
    """
    Get Random Forest Regression-based job readiness score for current user.
    This is an ADDITIONAL score alongside the existing TF-IDF based score.
    Returns 503 if RF model not trained.
    """
    try:
        db = get_firestore()
        uid = user["uid"]

        profile_doc = db.collection("profiles").document(uid).get()
        if not profile_doc.exists:
            raise HTTPException(status_code=404, detail="Profile not found")

        profile = profile_doc.to_dict() or {}
        profile["uid"] = uid

        from app.ml.model_registry import get_readiness_model
        model = get_readiness_model()

        if not model.is_trained:
            return {
                "model_available":    False,
                "message":            "RF Readiness model not yet trained. Call POST /api/ml/train first.",
                "prediction_method":  "random_forest_regression",
                "prediction_label":   "Random Forest Regression (not trained)",
            }

        result = model.predict(profile)
        if result is None:
            raise HTTPException(status_code=500, detail="Readiness prediction failed")

        result["model_available"] = True
        result["uid"] = uid
        result["generated_at"] = datetime.utcnow().isoformat()
        result["note"] = (
            "This score is predicted by a Random Forest Regression model trained on the "
            "students_database dataset (readiness_rating × 20 as proxy label). "
            "It may differ from the existing semantic TF-IDF score."
        )
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"RF readiness failed for uid={user.get('uid')}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ── GET /api/ml/career-rf ─────────────────────────────────────────────────────
@router.get("/career-rf")
async def get_rf_career_recommendations(
    top_n: int = Query(5, ge=1, le=10),
    user: dict = Depends(get_current_user),
):
    """
    Get Random Forest Classification-based career recommendations for current user.
    Returns top-N careers with probability scores.
    Returns 503 if RF model not trained.
    """
    try:
        db = get_firestore()
        uid = user["uid"]

        profile_doc = db.collection("profiles").document(uid).get()
        if not profile_doc.exists:
            raise HTTPException(status_code=404, detail="Profile not found")

        profile = profile_doc.to_dict() or {}
        profile["uid"] = uid

        from app.ml.model_registry import get_career_model
        model = get_career_model()

        if not model.is_trained:
            return {
                "model_available":    False,
                "message":            "Career RF model not yet trained. Call POST /api/ml/train first.",
                "prediction_method":  "random_forest_classification",
                "prediction_label":   "Random Forest Classification (not trained)",
                "recommendations":    [],
            }

        recommendations = model.predict_top_n(profile, top_n=top_n)
        if recommendations is None:
            raise HTTPException(status_code=500, detail="Career prediction failed")

        return {
            "model_available":   True,
            "uid":               uid,
            "recommendations":   recommendations,
            "prediction_method": CareerModel.PREDICTION_METHOD if hasattr(CareerModel, 'PREDICTION_METHOD') else "random_forest_classification",
            "prediction_label":  "Random Forest Classification",
            "generated_at":      datetime.utcnow().isoformat(),
            "note":              (
                "Careers are ranked by predicted probability from a Random Forest classifier "
                "trained on student career goal data. Probability scores reflect model confidence, "
                "not guaranteed career fit."
            ),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Career RF failed for uid={user.get('uid')}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ── GET /api/ml/skill-gap-enhanced ────────────────────────────────────────────
@router.get("/skill-gap-enhanced")
async def get_enhanced_skill_gap(
    career: Optional[str] = Query(None, description="Target career title (uses profile target if not specified)"),
    user: dict = Depends(get_current_user),
):
    """
    Get enhanced skill gap analysis using the authoritative career-skill mapping.
    Returns priority-classified missing skills, time estimates, and learning path summary.
    Method: Rule-Based Career Mapping (deterministic, explainable).
    """
    try:
        db = get_firestore()
        uid = user["uid"]

        profile_doc = db.collection("profiles").document(uid).get()
        if not profile_doc.exists:
            raise HTTPException(status_code=404, detail="Profile not found")

        profile = profile_doc.to_dict() or {}
        target_career = career or profile.get("target_career") or ""

        if not target_career:
            return {"message": "No target career specified", "gap": None}

        from app.ml.skill_gap_model import get_enhanced_skill_gap as _gap
        student_skills = profile.get("skills") or []
        result = _gap(student_skills, target_career)
        result["uid"] = uid

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Enhanced skill gap failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ── GET /api/ml/archetypes ────────────────────────────────────────────────────
@router.get("/archetypes")
async def get_all_archetypes():
    """
    Return all available student profile archetypes defined in the clustering model.
    Useful for UI display — no authentication required.
    """
    from app.ml.clustering_model import ARCHETYPES
    return {
        "archetypes": [
            {
                "id":          a["id"],
                "name":        a["name"],
                "icon":        a["icon"],
                "color":       a["color"],
                "description": a["description"],
                "career_fit":  a["career_fit"],
            }
            for a in ARCHETYPES
        ]
    }


# Fix forward reference to CareerModel
from app.ml.career_model import CareerModel
