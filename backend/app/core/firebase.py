"""
Firebase Admin SDK initialization
"""
import firebase_admin
from firebase_admin import credentials, firestore, storage, auth
import json
import os
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

_firebase_app = None


def init_firebase():
    global _firebase_app
    if _firebase_app:
        return _firebase_app

    try:
        # Try JSON string first (for deployment environments)
        if settings.FIREBASE_SERVICE_ACCOUNT_JSON:
            cred_dict = json.loads(settings.FIREBASE_SERVICE_ACCOUNT_JSON)
            cred = credentials.Certificate(cred_dict)
        elif os.path.exists(settings.FIREBASE_SERVICE_ACCOUNT_PATH):
            cred = credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT_PATH)
        else:
            logger.warning(
                "Firebase service account not found. "
                "Set FIREBASE_SERVICE_ACCOUNT_PATH or FIREBASE_SERVICE_ACCOUNT_JSON in .env"
            )
            return None

        _firebase_app = firebase_admin.initialize_app(
            cred,
            {"storageBucket": settings.FIREBASE_STORAGE_BUCKET},
        )
        logger.info("Firebase Admin SDK initialized")
        return _firebase_app

    except Exception as e:
        logger.error(f"Firebase initialization failed: {e}")
        return None


def get_firestore():
    """Return Firestore client."""
    return firestore.client()


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
