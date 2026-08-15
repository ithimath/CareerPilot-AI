"""
Firebase Admin SDK initialization
"""
import firebase_admin
from firebase_admin import credentials, firestore, storage, auth
import json
import os
import logging
from datetime import datetime
from app.core.config import settings

logger = logging.getLogger(__name__)

_firebase_app = None


class MockDocumentSnapshot:
    def __init__(self, doc_id, data):
        self.id = doc_id
        self._data = data
        self.exists = data is not None

    def to_dict(self):
        return self._data


class MockDocumentReference:
    def __init__(self, doc_id, path, client):
        self.id = doc_id
        self.path = path
        self.client = client

    def get(self):
        import copy
        data = self.client.db_store.get(self.path)
        if data is not None:
            data = copy.deepcopy(data)
        return MockDocumentSnapshot(self.id, data)

    def set(self, data):
        import copy
        self.client.db_store[self.path] = copy.deepcopy(data)
        self.client._persist()

    def update(self, data):
        import copy
        if self.path not in self.client.db_store:
            self.client.db_store[self.path] = {}
        self.client.db_store[self.path].update(copy.deepcopy(data))
        self.client._persist()

    def delete(self):
        self.client.db_store.pop(self.path, None)
        self.client._persist()

    def collection(self, collection_name):
        return MockCollectionReference(f"{self.path}/{collection_name}", self.client)


class MockCollectionReference:
    def __init__(self, path, client):
        self.path = path
        self.client = client
        self._limit = None
        self._order_field = None
        self._order_desc = False

    def document(self, doc_id=None):
        import uuid
        if not doc_id:
            doc_id = str(uuid.uuid4())
        return MockDocumentReference(doc_id, f"{self.path}/{doc_id}", self.client)

    def add(self, data, doc_id=None):
        import uuid
        if not doc_id:
            doc_id = str(uuid.uuid4())
        doc_ref = self.document(doc_id)
        doc_ref.set(data)
        return (None, doc_ref)

    def order_by(self, field, direction="ASCENDING"):
        self._order_field = field
        self._order_desc = (direction.upper() == "DESCENDING")
        return self

    def limit(self, count):
        self._limit = count
        return self

    def stream(self):
        prefix = f"{self.path}/"
        results = []
        for path, data in self.client.db_store.items():
            if path.startswith(prefix):
                subpath = path[len(prefix):]
                if "/" not in subpath:
                    doc = MockDocumentReference(subpath, path, self.client).get()
                    results.append(doc)
        if self._order_field:
            try:
                results.sort(
                    key=lambda d: (d.to_dict() or {}).get(self._order_field, ""),
                    reverse=self._order_desc
                )
            except Exception:
                pass
        if self._limit:
            results = results[:self._limit]
        return results

    def get(self):
        return self.stream()


class MockFirestoreClient:
    def __init__(self):
        self.datastore_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "data",
            "user_datastore.json"
        )
        self.db_store = self._load()

    def _load(self) -> dict:
        if os.path.exists(self.datastore_path):
            try:
                with open(self.datastore_path, "r", encoding="utf-8") as f:
                    store = json.load(f)
                    logger.info(f"Loaded {len(store)} documents from persistent datastore: {self.datastore_path}")
                    return store
            except Exception as e:
                logger.warning(f"Failed to load user_datastore.json: {e}")
        
        # Initial seed for dev-user-id only
        initial_store = {
            "profiles/dev-user-id": {
                "uid": "dev-user-id",
                "name": "Alex Morgan",
                "email": "alex.morgan@student.edu",
                "college": "Tech Institute of Technology",
                "degree": "B.Tech Computer Science",
                "department": "Computer Science & Engineering",
                "current_year": 3,
                "cgpa": 8.9,
                "target_career": "Full Stack Engineer",
                "skills": ["React", "TypeScript", "Python", "FastAPI", "Tailwind CSS", "SQL", "Git"],
                "interests": ["Artificial Intelligence", "Web Development", "System Architecture"],
                "github_url": "https://github.com/alexmorgan",
                "linkedin_url": "https://linkedin.com/in/alexmorgan",
                "portfolio_url": "https://alexmorgan.dev",
            },
            "jobScores/dev-user-id": {
                "uid": "dev-user-id",
                "total_score": 78.0,
                "skills_score": 24.0,
                "projects_score": 20.0,
                "internships_score": 15.0,
                "certificates_score": 7.0,
                "profile_score": 12.0,
                "suggestions": [
                    "Add 2 more certificates to boost your score above 85",
                    "Complete the System Architecture module in Learning Roadmap",
                    "Add measurable metrics (% performance gain) to resume project descriptions",
                ],
            },
            "chatHistory/dev-user-id/conversations/conv_1": {
                "id": "conv_1",
                "uid": "dev-user-id",
                "title": "Full Stack Engineer Learning Path",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "messages": [
                    {"role": "user", "content": "What technical skills should I master for Full-Stack role?", "timestamp": datetime.utcnow().isoformat()},
                    {"role": "assistant", "content": "To excel as a Full-Stack Engineer, you should master: React, TypeScript, Python, FastAPI, SQL, and Git.", "timestamp": datetime.utcnow().isoformat()}
                ]
            }
        }
        try:
            os.makedirs(os.path.dirname(self.datastore_path), exist_ok=True)
            with open(self.datastore_path, "w", encoding="utf-8") as f:
                json.dump(initial_store, f, indent=2, default=str)
        except Exception as e:
            logger.warning(f"Could not seed user_datastore.json: {e}")
        return initial_store

    def _persist(self):
        try:
            os.makedirs(os.path.dirname(self.datastore_path), exist_ok=True)
            with open(self.datastore_path, "w", encoding="utf-8") as f:
                json.dump(self.db_store, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error persisting user_datastore.json: {e}")

    def collection(self, collection_name):
        return MockCollectionReference(collection_name, self)


_mock_firestore_client = None


def init_firebase():
    global _firebase_app
    if _firebase_app:
        return _firebase_app

    try:
        # Try JSON string first (for deployment environments)
        if settings.FIREBASE_SERVICE_ACCOUNT_JSON:
            cred_dict = json.loads(settings.FIREBASE_SERVICE_ACCOUNT_JSON)
            cred = credentials.Certificate(cred_dict)
        elif settings.FIREBASE_SERVICE_ACCOUNT_PATH and os.path.exists(settings.FIREBASE_SERVICE_ACCOUNT_PATH):
            cred = credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT_PATH)
        else:
            logger.warning(
                "Firebase service account not found. "
                "Set FIREBASE_SERVICE_ACCOUNT_PATH or FIREBASE_SERVICE_ACCOUNT_JSON in .env. "
                "Running in Mock Firestore mode."
            )
            return None

        _firebase_app = firebase_admin.initialize_app(
            cred,
            {"storageBucket": settings.FIREBASE_STORAGE_BUCKET},
        )
        logger.info("Firebase Admin SDK initialized")
        return _firebase_app

    except Exception as e:
        logger.error(f"Firebase initialization failed: {e}. Running in Mock Firestore mode.")
        return None


def get_firestore():
    """Return Firestore client (real or mock)."""
    global _firebase_app, _mock_firestore_client
    if not _firebase_app:
        if _mock_firestore_client is None:
            _mock_firestore_client = MockFirestoreClient()
            logger.info("Mock Firestore Client initialized for development fallback")
        return _mock_firestore_client
    try:
        return firestore.client()
    except Exception as e:
        logger.warning(f"Failed to get production firestore client: {e}. Falling back to Mock Firestore.")
        if _mock_firestore_client is None:
            _mock_firestore_client = MockFirestoreClient()
        return _mock_firestore_client


def get_storage_bucket():
    """Return Firebase Storage bucket."""
    return storage.bucket()


def verify_id_token(id_token: str) -> dict:
    """Verify Firebase ID token and return decoded claims."""
    try:
        decoded = auth.verify_id_token(id_token)
        return decoded
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise ValueError(f"Invalid authentication token: {e}")
