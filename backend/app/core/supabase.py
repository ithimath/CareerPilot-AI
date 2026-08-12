"""
Supabase Backend initialization and token verification
"""
import logging
import jwt
from app.core.config import settings

logger = logging.getLogger(__name__)

_supabase_client = None

def init_supabase():
    global _supabase_client
    if settings.SUPABASE_URL and settings.SUPABASE_SERVICE_ROLE_KEY:
        try:
            from supabase import create_client
            _supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
            logger.info("Supabase Python client initialized successfully")
        except Exception as e:
            logger.warning(f"Supabase client initialization skipped/failed: {e}")
    else:
        logger.info("Supabase client initialized (development mode)")
    return _supabase_client


def verify_id_token(token: str) -> dict:
    """
    Verify Supabase Bearer token (JWT) and return decoded claims.
    """
    if not token:
        raise ValueError("Token missing")

    # If SUPABASE_JWT_SECRET is set, decode using secret
    if settings.SUPABASE_JWT_SECRET:
        try:
            decoded = jwt.decode(token, settings.SUPABASE_JWT_SECRET, algorithms=["HS256"], audience="authenticated")
            return {
                "uid": decoded.get("sub"),
                "email": decoded.get("email"),
                "user_metadata": decoded.get("user_metadata", {}),
                "sub": decoded.get("sub")
            }
        except Exception as e:
            logger.error(f"Supabase JWT verification failed: {e}")
            raise ValueError(f"Invalid Supabase auth token: {e}")

    # Development / Fallback decode unverified for local dev testing
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        return {
            "uid": decoded.get("sub", "dev-user-id"),
            "email": decoded.get("email", "student@example.com"),
            "user_metadata": decoded.get("user_metadata", {}),
            "sub": decoded.get("sub", "dev-user-id")
        }
    except Exception:
        # Fallback for dev mode
        return {
            "uid": "dev-user-id",
            "email": "student@example.com",
            "user_metadata": {"full_name": "Student User"},
            "sub": "dev-user-id"
        }
