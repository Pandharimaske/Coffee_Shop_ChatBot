from datetime import datetime
from typing import List
import logging

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from src.memory.supabase_client import supabase_admin as supabase

logger = logging.getLogger(__name__)

SESSIONS_TABLE  = "coffee_shop_sessions"
MESSAGES_TABLE  = "coffee_shop_messages"


# ── Sessions ──────────────────────────────────────────────────────────────────

def get_or_create_session(session_id: str, user_email: str) -> None:
    """Ensure session row exists, update last_active."""
    try:
        res = supabase.table(SESSIONS_TABLE).select("session_id").eq("session_id", session_id).execute()
        if res.data:
            supabase.table(SESSIONS_TABLE).update(
                {"last_active": datetime.now().isoformat()}
            ).eq("session_id", session_id).execute()
        else:
            supabase.table(SESSIONS_TABLE).insert({
                "session_id": session_id,
                "user_email": user_email,
                "created_at": datetime.now().isoformat(),
                "last_active": datetime.now().isoformat(),
            }).execute()
            logger.info(f"New session: {session_id} for {user_email}")
    except Exception as e:
        logger.error(f"get_or_create_session failed: {e}")


# ── Messages ──────────────────────────────────────────────────────────────────

def load_messages(session_id: str) -> List[BaseMessage]:
    """
    Load all messages for a session.
    Single row per session — messages stored as JSONB array.
    """
    try:
        res = (
            supabase.table(MESSAGES_TABLE)
            .select("messages")
            .eq("session_id", session_id)
            .execute()
        )
        if not res.data:
            return []

        raw = res.data[0].get("messages", [])
        result = []
        for m in raw:
            if m["role"] == "user":
                result.append(HumanMessage(content=m["content"]))
            elif m["role"] == "assistant":
                result.append(AIMessage(content=m["content"]))
        return result

    except Exception as e:
        logger.error(f"load_messages failed for session {session_id}: {e}")
        return []


def save_messages(session_id: str, user_email: str, user_input: str, bot_response: str) -> None:
    """
    Append one turn (user + assistant) to the session's message array.
    Upserts a single row per session.
    """
    try:
        now = datetime.now().isoformat()

        # Load existing messages
        res = (
            supabase.table(MESSAGES_TABLE)
            .select("messages")
            .eq("session_id", session_id)
            .execute()
        )

        existing = res.data[0]["messages"] if res.data else []

        # Append new turn
        updated = existing + [
            {"role": "user",      "content": user_input,    "timestamp": now},
            {"role": "assistant", "content": bot_response,  "timestamp": now},
        ]

        # Upsert single row
        supabase.table(MESSAGES_TABLE).upsert({
            "session_id": session_id,
            "user_email": user_email,
            "messages": updated,
            "updated_at": now,
        }, on_conflict="session_id").execute()

    except Exception as e:
        logger.error(f"save_messages failed for session {session_id}: {e}")
