"""
K-Means Clustering — Student Profiling Model
Groups students into human-readable profile archetypes based on their
skills, interests, academic background, and career preferences.
Number of clusters is configurable (default: 5).
"""
import os
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple

import numpy as np
import joblib
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from sklearn.pipeline import Pipeline

from app.ml.preprocessor import extract_features_from_live_profile, SKILL_VOCAB

logger = logging.getLogger(__name__)

# ── Paths ─────────────────────────────────────────────────────────────────────
_BACKEND_DIR  = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODELS_DIR    = os.path.join(_BACKEND_DIR, "models")
MODEL_PATH    = os.path.join(MODELS_DIR, "kmeans.joblib")
LABELS_PATH   = os.path.join(MODELS_DIR, "kmeans_labels.json")
META_PATH     = os.path.join(MODELS_DIR, "kmeans_metadata.json")

DEFAULT_N_CLUSTERS = 5

# ── Profile Archetype Definitions ─────────────────────────────────────────────
# Each archetype has a name, icon (emoji), description, and dominant skills.
# These are assigned dynamically based on cluster centroid analysis.
ARCHETYPES = [
    {
        "id":          "ai_ml_pioneer",
        "name":        "AI/ML Pioneer",
        "icon":        "🤖",
        "color":       "#8B5CF6",
        "description": "Strong focus on machine learning, deep learning, and AI engineering. Skilled in Python, TensorFlow, and data-driven model development.",
        "career_fit":  ["AI / Machine Learning Engineer", "Data Scientist"],
        "skill_signals": ["machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn", "nlp", "python"],
    },
    {
        "id":          "data_analytics_expert",
        "name":        "Data Analytics Expert",
        "icon":        "📊",
        "color":       "#0EA5E9",
        "description": "Proficient in data analysis, SQL, and visualization. Excels at translating data into insights using Python, R, Excel, and BI tools.",
        "career_fit":  ["Data Analyst", "Data Engineer", "Data Scientist"],
        "skill_signals": ["data analysis", "sql", "excel", "tableau", "power bi", "r", "python", "statistics"],
    },
    {
        "id":          "fullstack_builder",
        "name":        "Full-Stack Builder",
        "icon":        "⚡",
        "color":       "#10B981",
        "description": "Well-rounded in frontend and backend development. Comfortable with React, Node.js, databases, and REST API design.",
        "career_fit":  ["Full Stack Engineer", "Software Developer", "Backend Engineer", "Frontend Developer"],
        "skill_signals": ["react", "javascript", "node.js", "sql", "html", "css", "rest apis", "typescript"],
    },
    {
        "id":          "cloud_devops_engineer",
        "name":        "Cloud & DevOps Engineer",
        "icon":        "☁️",
        "color":       "#F59E0B",
        "description": "Infrastructure and automation focused. Strong in cloud platforms (AWS/GCP/Azure), containerization, and CI/CD pipelines.",
        "career_fit":  ["DevOps & Cloud Engineer", "Backend Engineer"],
        "skill_signals": ["aws", "docker", "kubernetes", "ci/cd", "terraform", "linux", "gcp", "azure"],
    },
    {
        "id":          "security_systems",
        "name":        "Security & Systems Specialist",
        "icon":        "🔒",
        "color":       "#EF4444",
        "description": "Focused on cybersecurity, network defense, and systems programming. Skilled in penetration testing, cryptography, and Linux.",
        "career_fit":  ["Cybersecurity Analyst"],
        "skill_signals": ["network security", "ethical hacking", "cryptography", "linux", "penetration testing"],
    },
]


def _identify_archetype_for_centroid(
    centroid: np.ndarray,
    n_skill_offset: int,
) -> Dict[str, Any]:
    """
    Identify the best-matching archetype for a K-Means cluster centroid.
    Uses dot-product similarity between centroid skill vector and archetype signals.
    """
    # The multi-hot skill features start at offset `n_skill_offset`
    centroid_skills = centroid[n_skill_offset:]  # shape: (len(SKILL_VOCAB),)

    best_score = -1.0
    best_archetype = ARCHETYPES[0]

    for archetype in ARCHETYPES:
        signal_vec = np.zeros(len(SKILL_VOCAB), dtype=np.float32)
        for sig_skill in archetype["skill_signals"]:
            if sig_skill in [s.lower() for s in SKILL_VOCAB]:
                # Find index
                for i, vocab_skill in enumerate(SKILL_VOCAB):
                    if vocab_skill.lower() == sig_skill:
                        signal_vec[i] = 1.0
                        break

        score = float(np.dot(centroid_skills, signal_vec))
        if score > best_score:
            best_score = score
            best_archetype = archetype

    return best_archetype


class ClusteringModel:
    """
    K-Means Clustering model for student profiling.
    Maps raw cluster IDs to human-readable archetypes.
    """

    PREDICTION_METHOD = "kmeans_clustering"

    def __init__(self, n_clusters: int = DEFAULT_N_CLUSTERS):
        self.n_clusters = n_clusters
        self._pipeline: Optional[Pipeline] = None
        self._cluster_labels: Dict[int, Dict[str, Any]] = {}
        self._metadata: Dict[str, Any] = {}
        os.makedirs(MODELS_DIR, exist_ok=True)

    @property
    def is_trained(self) -> bool:
        return self._pipeline is not None and bool(self._cluster_labels)

    def train(self, X_train, n_clusters: Optional[int] = None) -> Dict[str, Any]:
        """
        Train K-Means on the full training set (unsupervised — no labels needed).
        Returns metrics dict including Silhouette Score.
        """
        if n_clusters:
            self.n_clusters = n_clusters

        logger.info(f"Training ClusteringModel with n_clusters={self.n_clusters} on {len(X_train)} samples...")

        pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("kmeans", KMeans(
                n_clusters=self.n_clusters,
                init="k-means++",
                n_init=20,
                max_iter=500,
                random_state=42,
            )),
        ])

        labels = pipeline.fit_predict(X_train)
        self._pipeline = pipeline

        # Silhouette score (needs at least 2 unique labels)
        if len(set(labels)) > 1:
            sil_score = float(silhouette_score(
                pipeline.named_steps["scaler"].transform(X_train),
                labels,
                sample_size=min(len(X_train), 2000),
                random_state=42,
            ))
        else:
            sil_score = 0.0

        # Map each cluster ID to a human-readable archetype
        # Use approximate centroid offsets (7 aggregates + 6 course = 13 before skills)
        n_skill_offset = 13
        kmeans = pipeline.named_steps["kmeans"]
        scaler = pipeline.named_steps["scaler"]

        # Centroids are in scaled space — inverse-transform to get feature-space centroids
        centroids_scaled = kmeans.cluster_centers_
        try:
            centroids_orig = scaler.inverse_transform(centroids_scaled)
        except Exception:
            centroids_orig = centroids_scaled

        # Assign archetypes — ensure uniqueness by a greedy assignment
        assigned_archetypes: Dict[int, Dict] = {}
        archetype_scores: List[Tuple[int, int, float]] = []  # (cluster_id, archetype_idx, score)

        for cluster_id in range(self.n_clusters):
            centroid = centroids_orig[cluster_id] if cluster_id < len(centroids_orig) else np.zeros(centroids_orig.shape[1])
            centroid_skills = centroid[n_skill_offset:] if len(centroid) > n_skill_offset else centroid

            for arch_idx, archetype in enumerate(ARCHETYPES):
                signal_vec = np.zeros(len(SKILL_VOCAB), dtype=np.float32)
                for sig_skill in archetype["skill_signals"]:
                    for i, vocab_skill in enumerate(SKILL_VOCAB):
                        if vocab_skill.lower() == sig_skill.lower():
                            signal_vec[i] = 1.0
                            break
                score = float(np.dot(centroid_skills[:len(signal_vec)], signal_vec))
                archetype_scores.append((cluster_id, arch_idx, score))

        # Greedy assignment: highest-score first
        archetype_scores.sort(key=lambda x: x[2], reverse=True)
        used_archetypes: set = set()
        for cluster_id in range(self.n_clusters):
            assigned_archetypes[cluster_id] = None

        for cluster_id, arch_idx, score in archetype_scores:
            if assigned_archetypes[cluster_id] is None and arch_idx not in used_archetypes:
                assigned_archetypes[cluster_id] = ARCHETYPES[arch_idx]
                used_archetypes.add(arch_idx)

        # Fill any unassigned clusters with cycled archetypes
        remaining_archetypes = [a for i, a in enumerate(ARCHETYPES) if i not in used_archetypes]
        for cluster_id in range(self.n_clusters):
            if assigned_archetypes[cluster_id] is None:
                if remaining_archetypes:
                    assigned_archetypes[cluster_id] = remaining_archetypes.pop(0)
                else:
                    # Cycle through all archetypes for extra clusters
                    assigned_archetypes[cluster_id] = ARCHETYPES[cluster_id % len(ARCHETYPES)]

        self._cluster_labels = {int(k): v for k, v in assigned_archetypes.items()}

        self._metadata = {
            "model_type":    "KMeans",
            "n_clusters":    self.n_clusters,
            "train_samples": int(len(X_train)),
            "metrics": {
                "silhouette_score": round(sil_score, 4),
                "inertia": round(float(kmeans.inertia_), 2),
            },
            "cluster_archetypes": {
                str(k): {
                    "archetype_id":   v["id"],
                    "archetype_name": v["name"],
                    "color":          v["color"],
                }
                for k, v in self._cluster_labels.items()
            },
            "trained_at":    datetime.utcnow().isoformat(),
            "prediction_method": self.PREDICTION_METHOD,
        }

        logger.info(
            f"ClusteringModel trained — n_clusters={self.n_clusters}, "
            f"Silhouette={sil_score:.4f}"
        )
        return self._metadata["metrics"]

    def assign_cluster(self, profile: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Assign a student profile to a cluster.
        Returns dict with cluster_id, archetype, characteristics.
        Returns None if model not trained.
        """
        if not self.is_trained:
            return None

        try:
            features = extract_features_from_live_profile(profile)
            import pandas as pd
            X = pd.DataFrame(features.reshape(1, -1), columns=FEATURE_NAMES)

            cluster_id = int(self._pipeline.predict(X)[0])
            archetype  = self._cluster_labels.get(cluster_id, ARCHETYPES[0])

            return {
                "cluster_id":           cluster_id,
                "archetype_id":         archetype["id"],
                "archetype_name":       archetype["name"],
                "archetype_icon":       archetype["icon"],
                "archetype_color":      archetype["color"],
                "description":          archetype["description"],
                "career_fit":           archetype["career_fit"],
                "prediction_method":    self.PREDICTION_METHOD,
                "prediction_label":     "K-Means Clustering",
                "note":                 (
                    f"You belong to cluster #{cluster_id + 1} of {self.n_clusters}. "
                    "This is determined by grouping students with similar skill profiles using K-Means Clustering."
                ),
            }
        except Exception as e:
            logger.error(f"ClusteringModel.assign_cluster() failed: {e}", exc_info=True)
            return None

    def save(self) -> None:
        """Persist model and labels to disk."""
        if not self.is_trained:
            raise RuntimeError("Cannot save — model not trained")
        joblib.dump(self._pipeline, MODEL_PATH)
        serializable_labels = {
            str(k): v for k, v in self._cluster_labels.items()
        }
        with open(LABELS_PATH, "w", encoding="utf-8") as f:
            json.dump(serializable_labels, f, indent=2)
        with open(META_PATH, "w", encoding="utf-8") as f:
            json.dump(self._metadata, f, indent=2, default=str)
        logger.info(f"ClusteringModel saved to {MODEL_PATH}")

    def load(self) -> bool:
        """Load persisted model. Returns True if successful."""
        if not os.path.exists(MODEL_PATH):
            return False
        try:
            self._pipeline = joblib.load(MODEL_PATH)
            if os.path.exists(LABELS_PATH):
                with open(LABELS_PATH, "r", encoding="utf-8") as f:
                    raw_labels = json.load(f)
                self._cluster_labels = {int(k): v for k, v in raw_labels.items()}
            if os.path.exists(META_PATH):
                with open(META_PATH, "r", encoding="utf-8") as f:
                    self._metadata = json.load(f)
                self.n_clusters = self._metadata.get("n_clusters", DEFAULT_N_CLUSTERS)
            logger.info(f"ClusteringModel loaded — n_clusters={self.n_clusters}")
            return True
        except Exception as e:
            logger.error(f"Failed to load ClusteringModel: {e}")
            self._pipeline = None
            self._cluster_labels = {}
            return False

    def get_metadata(self) -> Dict[str, Any]:
        return dict(self._metadata)

    def get_all_archetypes(self) -> List[Dict[str, Any]]:
        """Return all cluster-to-archetype mappings."""
        return [
            {"cluster_id": k, **v}
            for k, v in sorted(self._cluster_labels.items())
        ]
