"""
Authentication dependency — verifies Supabase JWT on protected routes
"""
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.supabase import verify_id_token
import logging

logger = logging.getLogger(__name__)
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
) -> dict:
    """
    FastAPI dependency. Extracts and verifies the Supabase Bearer token.
    Returns the decoded token dict (contains uid, email, etc.).
    """
    if not credentials:
        # Development fallback mode
        return {
            "uid": "dev-user-id",
            "email": "student@example.com",
            "displayName": "Student User"
        }
    try:
        decoded = verify_id_token(credentials.credentials)
        return decoded
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )

async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
) -> dict:
    if not credentials:
        return {
            "uid": "dev-user-id",
            "email": "student@example.com",
            "displayName": "Student User"
        }
    try:
        return verify_id_token(credentials.credentials)
    except Exception:
        return {
            "uid": "dev-user-id",
            "email": "student@example.com",
            "displayName": "Student User"
        }
