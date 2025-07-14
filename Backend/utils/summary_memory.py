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
    response = supabase.table("Summaries").select("messages").eq("id", id).execute()
    data = response.data[0]["messages"]
    return [
        HumanMessage(content=m["content"]) if m["role"] == "human" else AIMessage(content=m["content"])
        for m in data
    ]

def save_messages(id: int, messages: list[BaseMessage]):
    serialized = serialize_messages(messages)
    supabase.table("Summaries").update({
        "messages": serialized
    }).eq("id", id).execute()



def get_summary(id: int) -> str:
    res = supabase.table("Summaries").select("summary").eq("id", id).execute()
    return res.data[0]["summary"] if res.data else ""


def save_summary(id: int, summary: str):
    supabase.table("Summaries").upsert({
        "id": id,
        "summary": summary,
        "last_updated": datetime.now().isoformat()
    }).execute()