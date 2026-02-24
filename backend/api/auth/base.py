from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class UserRecord:
    id: str           # provider user id (uuid string)
    email: str
    username: Optional[str] = None


@dataclass
class TokenPair:
    access_token: str
    token_type: str = "bearer"


class AuthProvider(ABC):

    @abstractmethod
    async def register(self, email: str, password: str, username: str) -> UserRecord:
        """Create a new user. Raises ValueError on duplicate."""

    @abstractmethod
    async def login(self, email: str, password: str) -> TokenPair:
        """Authenticate and return tokens. Raises ValueError on bad credentials."""

    @abstractmethod
    async def verify_token(self, token: str) -> str:
        """Validate token and return user_id. Raises ValueError if invalid."""

    @abstractmethod
    async def get_user(self, user_id: str) -> UserRecord:
        """Fetch user record by id. Raises ValueError if not found."""

    async def get_user_from_token(self, token: str) -> UserRecord:
        """
        Verify token and return UserRecord in one step.
        Default: two-step (verify_token + get_user).
        Override in providers that can do it in one call (e.g. Supabase).
        """
        user_id = await self.verify_token(token)
        return await self.get_user(user_id)
