from Backend.memory.supabase_client import supabase
from datetime import datetime

def get_summary(id: int) -> str:
    res = supabase.table("summaries").select("summary").eq("id", id).execute()
    return res.data[0]["summary"] if res.data else ""


def save_summary(id: int, summary: str):
    supabase.table("summaries").upsert({
        "id": id,
        "summary": summary,
        "last_updated": datetime.utcnow().isoformat()
    }).execute()
    