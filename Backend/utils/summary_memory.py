from Backend.memory.supabase_client import supabase
from datetime import datetime
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

def serialize_messages(messages: list[BaseMessage]) -> list[dict]:
    return [
        {
            "role": "human" if isinstance(m, HumanMessage) else "ai",
            "content": m.content
        }
        for m in messages
    ]


def get_messages(id: int) -> list[BaseMessage]:
    response = supabase.table("summaries").select("messages").eq("id", id).execute()
    data = response.data[0]["messages"] if response.data else None
    return [
        HumanMessage(content=m["content"]) if m["role"] == "human" else AIMessage(content=m["content"])
        for m in data
    ]

def save_messages(id: int, messages: list[BaseMessage]):
    serialized = serialize_messages(messages)
    supabase.table("summaries").update({
        "messages": serialized
    }).eq("id", id).execute()



def get_summary(id: int) -> str:
    res = supabase.table("summaries").select("summary").eq("id", id).execute()
    return res.data[0]["summary"] if res.data else ""


def save_summary(id: int, summary: str):
    supabase.table("summaries").upsert({
        "id": id,
        "summary": summary,
        "last_updated": datetime.now().isoformat()
    }).execute()