"""
Authentication dependency — verifies Supabase JWT on protected routes
"""
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.supabase import verify_id_token
import logging

from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
) -> dict:
    """
    FastAPI dependency. Extracts and verifies the Supabase Bearer token.
    Returns the decoded token dict (contains uid, email, etc.).
    Rejects unauthenticated requests with 401.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        decoded = verify_id_token(credentials.credentials)
        if not decoded or not decoded.get("uid"):
            raise ValueError("Token does not contain valid user identity")
        return decoded
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
) -> Optional[dict]:
    """
    Optional authentication dependency.
    Returns decoded user dict if a valid token is provided, or None if unauthenticated.
    """
    if not credentials or not credentials.credentials:
        return None
    try:
        decoded = verify_id_token(credentials.credentials)
        return decoded if decoded and decoded.get("uid") else None
    except Exception:
        return None

