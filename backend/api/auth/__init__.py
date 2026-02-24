"""Auth provider loader — reads AUTH_PROVIDER from config and loads the right adapter."""

import logging
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from api.auth.base import AuthProvider, UserRecord, TokenPair
from api.config import settings

logger = logging.getLogger(__name__)


def _load_provider() -> AuthProvider:
    provider = getattr(settings, "auth_provider", "supabase").lower()
    if provider == "supabase":
        from api.auth.supabase_auth import SupabaseAuthProvider
        logger.info("Using Supabase auth provider")
        return SupabaseAuthProvider()
    elif provider == "aws":
        from api.auth.aws_auth import CognitoAuthProvider
        logger.info("Using AWS Cognito auth provider")
        return CognitoAuthProvider()
    else:
        raise ValueError(f"Unknown auth provider: {provider}")


auth: AuthProvider = _load_provider()

_bearer = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer)],
) -> UserRecord:
    """
    FastAPI dependency — validates Bearer token and returns UserRecord.
    Single Supabase call: get_user_from_token does verify + fetch in one shot.
    """
    try:
        # Use get_user_from_token if available (Supabase), else fall back to two-step
        if hasattr(auth, "get_user_from_token"):
            return await auth.get_user_from_token(credentials.credentials)
        else:
            user_id = await auth.verify_token(credentials.credentials)
            return await auth.get_user(user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


CurrentUser = Annotated[UserRecord, Depends(get_current_user)]

__all__ = ["auth", "get_current_user", "CurrentUser", "UserRecord", "TokenPair"]
