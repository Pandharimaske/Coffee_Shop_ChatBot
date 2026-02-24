"""AWS Cognito auth adapter — stub for future migration."""

import logging
from api.auth.base import AuthProvider, UserRecord, TokenPair

logger = logging.getLogger(__name__)


class CognitoAuthProvider(AuthProvider):

    async def register(self, email: str, password: str, username: str) -> UserRecord:
        raise NotImplementedError("AWS Cognito auth not yet implemented")

    async def login(self, email: str, password: str) -> TokenPair:
        raise NotImplementedError("AWS Cognito auth not yet implemented")

    async def verify_token(self, token: str) -> str:
        raise NotImplementedError("AWS Cognito auth not yet implemented")

    async def get_user(self, user_id: str) -> UserRecord:
        raise NotImplementedError("AWS Cognito auth not yet implemented")
