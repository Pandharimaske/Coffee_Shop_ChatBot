from datetime import datetime
from typing import Dict

from Backend.memory.user_memory import UserMemory
from Backend.memory.supabase_client import supabase


def get_user_memory(user_id: int) -> UserMemory:
    """Fetch user memory from Supabase, or create it with defaults if not present."""

    res = supabase.table("user_profiles").select("*").eq("id", user_id).execute()

    if not res.data:
        # Create default user memory
        default_data = {
            "id": user_id,            # assuming 'id' is the primary key in the table
            "name": None,
            "likes": [],
            "dislikes": [],
            "allergies": [],
            "last_order": None,
            "feedback": [],
            "location": None
        }

        supabase.table("user_profiles").insert(default_data).execute()
        return UserMemory(**{k: v for k, v in default_data.items() if k in UserMemory.__fields__})

    return UserMemory(**res.data[0])


def save_user_memory(user_id: int, memory: UserMemory):
    """Upsert full user memory into Supabase."""
    data = memory.dict()
    data["id"] = user_id
    data["last_updated"] = datetime.now().isoformat()
    supabase.table("user_profiles").upsert(data).execute()


def merge_and_update_memory(updates: Dict , existing:UserMemory) -> UserMemory:
    """Merge list fields and overwrite scalar fields, then save."""

    for key, new_val in updates.items():
        if isinstance(new_val, list):
            current = getattr(existing, key, [])
            merged = list(set(current + new_val))
            setattr(existing, key, merged)
        else:
            setattr(existing, key, new_val)
    return existing


def remove_from_memory(to_remove: Dict , existing:UserMemory) -> UserMemory:
    """Remove items from list fields or nullify scalar fields, then save."""

    for key, values in to_remove.items():
        if isinstance(values, list) and hasattr(existing, key):
            current = getattr(existing, key, [])
            filtered = [v for v in current if v.lower() not in map(str.lower, values)]
            setattr(existing, key, filtered)
        elif isinstance(values, str) and hasattr(existing, key):
            if getattr(existing, key) == values:
                setattr(existing, key, None)

    return existing