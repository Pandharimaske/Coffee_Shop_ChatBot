from datetime import datetime, timezone
from typing import Dict, Any

from src.memory.schemas import UserMemory
from src.memory.supabase_client import supabase_admin as supabase

import logging
logger = logging.getLogger(__name__)

TABLE = "coffee_shop_profiles"


def get_user_memory(user_email: str) -> UserMemory:
    """Fetch user memory from Supabase. Creates default row if not present."""
    email = str(user_email).lower().strip()
    try:
        res = supabase.table(TABLE).select("*").eq("user_email", email).execute()

        if not res.data:
            default_data = {
                "user_email": email,
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
    email = str(user_email).lower().strip()
    try:
        data = memory.model_dump()
        data["user_email"] = email
        data["last_updated"] = datetime.now(timezone.utc).isoformat()
        
        # EXTREME LOGGING for debugging
        logger.info(f"--- UPSERT ATTEMPT: {TABLE} ---")
        logger.info(f"Target Email: {email}")
        logger.info(f"Payload: {data}")
        
        res = supabase.table(TABLE).upsert(data, on_conflict="user_email").execute()
        
        logger.info(f"Supabase Response: {res}")
        
        if hasattr(res, 'error') and res.error:
            logger.error(f"save_user_memory DB ERROR for {email}: {res.error}")
        else:
            logger.info(f"Memory synced to '{TABLE}' table for {email} ✅")
    except Exception as e:
        logger.error(f"save_user_memory exception for {email}: {e}", exc_info=True)


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
        
        # Normalize incoming 'values' to a set of strings for list fields
        if isinstance(current, list):
            # Handle both list and string inputs for list fields
            if isinstance(values, list):
                to_remove_set = {str(x).lower().strip() for x in values}
            else:
                to_remove_set = {str(values).lower().strip()}
                
            filtered = [
                v for v in current 
                if str(v).lower().strip() not in to_remove_set
            ]
            setattr(existing, key, filtered)
            
        elif isinstance(values, str) and str(current).lower().strip() == str(values).lower().strip():
            setattr(existing, key, None)
            
    return existing


def replace_in_memory(replacements: Dict[str, Any], existing: UserMemory) -> UserMemory:
    """Completely replace fields."""
    for key, value in replacements.items():
        if hasattr(existing, key):
            setattr(existing, key, value)
    return existing
