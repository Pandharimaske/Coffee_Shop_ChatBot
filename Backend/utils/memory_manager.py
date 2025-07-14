from datetime import datetime
from typing import Dict

from Backend.memory.user_memory import UserMemory
from Backend.memory.supabase_client import supabase


def get_user_memory(user_id: int) -> UserMemory:
    """Fetch user memory from Supabase."""
    res = supabase.table("user_profiles").select("*").eq("id", user_id).execute()
    data = res.data[0] if res.data else {}
    return UserMemory(**data)


def save_user_memory(user_id: int, memory: UserMemory):
    """Upsert full user memory into Supabase."""
    data = memory.dict()
    data["id"] = user_id
    data["last_updated"] = datetime.now().isoformat()
    supabase.table("user_profiles").upsert(data).execute()


def merge_and_update_memory(user_id: int, updates: Dict) -> UserMemory:
    """Merge list fields and overwrite scalar fields, then save."""
    existing = get_user_memory(user_id)

    for key, new_val in updates.items():
        if isinstance(new_val, list):
            current = getattr(existing, key, [])
            merged = list(set(current + new_val))
            setattr(existing, key, merged)
        else:
            setattr(existing, key, new_val)

    save_user_memory(user_id, existing)
    return existing


def remove_from_memory(user_id: int, to_remove: Dict) -> UserMemory:
    """Remove items from list fields or nullify scalar fields, then save."""
    existing = get_user_memory(user_id)

    for key, values in to_remove.items():
        if isinstance(values, list) and hasattr(existing, key):
            current = getattr(existing, key, [])
            filtered = [v for v in current if v.lower() not in map(str.lower, values)]
            setattr(existing, key, filtered)
        elif isinstance(values, str) and hasattr(existing, key):
            if getattr(existing, key) == values:
                setattr(existing, key, None)

    save_user_memory(user_id, existing)
    return existing