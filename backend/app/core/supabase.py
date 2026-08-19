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


def get_supabase_client():
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = init_supabase()
    return _supabase_client


def verify_id_token(token: str) -> dict:
    """
    Verify Supabase Bearer token (JWT) and return decoded claims.
    """
    if not token or not isinstance(token, str):
        raise ValueError("Token missing or invalid")

    # Clean bearer prefix if accidentally included
    if token.startswith("Bearer "):
        token = token[7:].strip()

    # 1. If SUPABASE_JWT_SECRET is set, strictly verify using HS256
    if settings.SUPABASE_JWT_SECRET:
        try:
            # First attempt with audience="authenticated"
            try:
                decoded = jwt.decode(
                    token,
                    settings.SUPABASE_JWT_SECRET,
                    algorithms=["HS256"],
                    audience="authenticated"
                )
            except jwt.InvalidAudienceError:
                # Some Supabase projects may issue tokens without audience constraint
                decoded = jwt.decode(
                    token,
                    settings.SUPABASE_JWT_SECRET,
                    algorithms=["HS256"],
                    options={"verify_aud": False}
                )

            uid = decoded.get("sub")
            if not uid:
                raise ValueError("Token missing subject claim (sub)")

            return {
                "uid": uid,
                "email": decoded.get("email", ""),
                "name": decoded.get("user_metadata", {}).get("full_name") or decoded.get("user_metadata", {}).get("display_name", ""),
                "user_metadata": decoded.get("user_metadata", {}),
                "sub": uid
            }
        except Exception as e:
            logger.warning(f"Supabase JWT cryptographic verification failed: {e}")
            raise ValueError(f"Invalid Supabase auth token: {e}")

    # 2. If in production and no JWT secret configured, reject
    if settings.is_production:
        logger.error("SUPABASE_JWT_SECRET must be configured in production environment.")
        raise ValueError("Authentication service unconfigured for production")

    # 3. Development / Fallback decode for local testing
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        uid = decoded.get("sub")
        if not uid:
            raise ValueError("Token missing subject (sub)")
        return {
            "uid": uid,
            "email": decoded.get("email", "student@example.com"),
            "name": decoded.get("user_metadata", {}).get("full_name") or decoded.get("user_metadata", {}).get("display_name", "Student User"),
            "user_metadata": decoded.get("user_metadata", {}),
            "sub": uid
        }
    except Exception as e:
        logger.warning(f"Token decoding failed: {e}")
        raise ValueError(f"Invalid token structure: {e}")

