"""Supabase Auth adapter."""

import asyncio
import logging
from api.auth.base import AuthProvider, UserRecord, TokenPair
from src.memory.supabase_client import supabase

logger = logging.getLogger(__name__)

# How long (seconds) we wait for a single Supabase auth call
_AUTH_TIMEOUT = 12


def _parse_user(user) -> UserRecord:
    username = (user.user_metadata or {}).get("username")
    return UserRecord(id=user.id, email=user.email, username=username)


async def _run(fn, *args, label: str = "supabase"):
    """Run a blocking Supabase call in a thread with a timeout."""
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(fn, *args),
            timeout=_AUTH_TIMEOUT,
        )
    except asyncio.TimeoutError:
        logger.error(f"{label} timed out after {_AUTH_TIMEOUT}s — is your Supabase project paused?")
        raise ValueError(
            "Cannot reach Supabase right now. "
            "If you're on the free tier, your project may be paused — "
            "visit https://supabase.com/dashboard to resume it."
        )
    except Exception as e:
        logger.error(f"{label} failed: {e}")
        raise


class SupabaseAuthProvider(AuthProvider):

    async def register(self, email: str, password: str, username: str) -> UserRecord:
        try:
            res = await _run(
                supabase.auth.sign_up,
                {"email": email, "password": password, "options": {"data": {"username": username}}},
                label="Supabase register",
            )
            if not res.user:
                raise ValueError("Registration failed — no user returned. The email may already be in use.")
            return _parse_user(res.user)
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Registration error: {e}")

    async def login(self, email: str, password: str) -> TokenPair:
        try:
            res = await _run(
                supabase.auth.sign_in_with_password,
                {"email": email, "password": password},
                label="Supabase login",
            )
            if not res.session:
                raise ValueError("Invalid email or password")
            return TokenPair(access_token=res.session.access_token)
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Login error: {e}")

    async def verify_token(self, token: str) -> str:
        try:
            res = await _run(supabase.auth.get_user, token, label="Supabase verify_token")
            if not res.user:
                raise ValueError("Invalid or expired token")
            return res.user.id
        except ValueError:
            raise
        except Exception as e:
            raise ValueError("Invalid or expired token")

    async def get_user(self, user_id: str) -> UserRecord:
        raise NotImplementedError("Use get_user_from_token instead")

    async def get_user_from_token(self, token: str) -> UserRecord:
        try:
            res = await _run(supabase.auth.get_user, token, label="Supabase get_user_from_token")
            if not res.user:
                raise ValueError("Invalid or expired token")
            return _parse_user(res.user)
        except ValueError:
            raise
        except Exception as e:
            raise ValueError("Invalid or expired token")
