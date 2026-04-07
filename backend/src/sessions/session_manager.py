from datetime import datetime, timezone
from typing import List
import logging

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from src.memory.supabase_client import supabase_admin as supabase

logger = logging.getLogger(__name__)

SESSIONS_TABLE  = "coffee_shop_sessions"

# ── Sessions ──────────────────────────────────────────────────────────────────

def get_or_create_session(session_id: str, user_email: str) -> None:
    """Ensure session row exists, update last_active."""
    sid = str(session_id).lower().strip()
    email = str(user_email).lower().strip()
    try:
        res = supabase.table(SESSIONS_TABLE).select("session_id").eq("session_id", sid).execute()
        if res.data:
            supabase.table(SESSIONS_TABLE).update(
                {"last_active": datetime.now(timezone.utc).isoformat()}
            ).eq("session_id", sid).execute()
        else:
            supabase.table(SESSIONS_TABLE).insert({
                "session_id": sid,
                "user_email": email,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_active": datetime.now(timezone.utc).isoformat(),
            }).execute()
            logger.info(f"New session: {sid} for {email}")
    except Exception as e:
        logger.error(f"get_or_create_session failed: {e}")


# ── Messages ──────────────────────────────────────────────────────────────────

def load_messages(session_id: str) -> List[BaseMessage]:
    """
    Load all messages for a session.
    Single row per session — messages stored as JSONB array.
    """
    sid = str(session_id).lower().strip()
    try:
        res = (
            supabase.table(SESSIONS_TABLE)
            .select("messages")
            .eq("session_id", sid)
            .execute()
        )
        if not res.data:
            return []

        raw = res.data[0].get("messages", [])
        result = []
        for m in raw:
            role = str(m.get("role", "")).lower()
            content = m.get("content", "")
            
            if role in ("user", "human"):
                result.append(HumanMessage(content=content))
            elif role in ("assistant", "bot"):
                result.append(AIMessage(content=content))
        return result

    except Exception as e:
        logger.error(f"load_messages failed for session {session_id}: {e}")
        return []


def append_messages(session_id: str, user_email: str, new_messages: List[dict]) -> None:
    """
    Append multiple messages atomically using a Supabase RPC.
    Eliminates all race conditions by doing the 'append' on the database side.
    """
    sid = str(session_id).lower().strip()
    email = str(user_email).lower().strip()
    now = datetime.now(timezone.utc).isoformat()
    
    try:
        # Prepare the payload for JSONB concatenation
        to_add = []
        for m in new_messages:
            to_add.append({
                "role": m["role"].lower(),
                "content": m["content"],
                "timestamp": now
            })
            
        # CALL ATOMIC RPC: append_chat_messages(p_session_id, p_user_email, p_new_messages)
        res = supabase.rpc("append_chat_messages", {
            "p_session_id": sid,
            "p_user_email": email,
            "p_new_messages": to_add
        }).execute()
        
        if hasattr(res, 'error') and res.error:
            logger.error(f"RPC append_chat_messages failed for {sid}: {res.error}")
            # NO FALLBACK TO READ-MODIFY-WRITE (It is unsafe and causes the race condition)
        else:
            logger.info(f"Atomic messages appended for session {sid} ✅")
            
    except Exception as e:
        logger.error(f"append_messages exception for session {sid}: {e}")


def append_message(session_id: str, user_email: str, role: str, content: str) -> None:
    """
    Append a single message (atomic).
    """
    append_messages(session_id, user_email, [{"role": role, "content": content}])


def save_messages(session_id: str, user_email: str, user_input: str, bot_response: str) -> None:
    """
    Compatibility function — appends a turn (User + Bot) atomically.
    """
    append_messages(session_id, user_email, [
        {"role": "user", "content": user_input},
        {"role": "bot", "content": bot_response}
    ])
