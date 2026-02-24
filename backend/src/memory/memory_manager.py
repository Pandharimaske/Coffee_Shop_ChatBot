from datetime import datetime
from typing import Dict, Any

from src.memory.schemas import UserMemory
from src.memory.supabase_client import supabase_admin as supabase

import logging
logger = logging.getLogger(__name__)

TABLE = "coffee_shop_profiles"


def get_user_memory(user_email: str) -> UserMemory:
    """Fetch user memory from Supabase. Creates default row if not present."""
    try:
        res = supabase.table(TABLE).select("*").eq("user_email", user_email).execute()

        if not res.data:
            default_data = {
                "user_email": user_email,
                "name": None,
                "likes": [],
                "dislikes": [],
                "allergies": [],
                "last_order": None,
                "feedback": [],
                "location": None,
            }
            supabase.table(TABLE).insert(default_data).execute()
            return UserMemory()

        row = res.data[0]
        valid_fields = UserMemory.model_fields.keys()
        return UserMemory(**{k: v for k, v in row.items() if k in valid_fields})

    except Exception as e:
        logger.error(f"get_user_memory failed for {user_email}: {e}")
        return UserMemory()


def save_user_memory(user_email: str, memory: UserMemory) -> None:
    """Upsert full user memory to Supabase."""
    try:
        data = memory.model_dump()
        data["user_email"] = user_email
        data["last_updated"] = datetime.now().isoformat()
        supabase.table(TABLE).upsert(data, on_conflict="user_email").execute()
        logger.info(f"Memory saved for {user_email}")
    except Exception as e:
        logger.error(f"save_user_memory failed for {user_email}: {e}")


def merge_and_update_memory(updates: Dict[str, Any], existing: UserMemory) -> UserMemory:
    """Append list fields, overwrite scalar fields."""
    for key, new_val in updates.items():
        if not hasattr(existing, key):
            continue
        if isinstance(new_val, list):
            current = getattr(existing, key) or []
            merged = list(dict.fromkeys(current + new_val))
            setattr(existing, key, merged)
        else:
            setattr(existing, key, new_val)
    return existing


def remove_from_memory(to_remove: Dict[str, Any], existing: UserMemory) -> UserMemory:
    """Remove items from list fields or nullify scalar fields."""
    for key, values in to_remove.items():
        if not hasattr(existing, key):
            continue
        current = getattr(existing, key)
        if isinstance(values, list) and isinstance(current, list):
            filtered = [v for v in current if v.lower() not in {x.lower() for x in values}]
            setattr(existing, key, filtered)
        elif isinstance(values, str) and current == values:
            setattr(existing, key, None)
    return existing


def replace_in_memory(replacements: Dict[str, Any], existing: UserMemory) -> UserMemory:
    """Completely replace fields."""
    for key, value in replacements.items():
        if hasattr(existing, key):
            setattr(existing, key, value)
    return existing
