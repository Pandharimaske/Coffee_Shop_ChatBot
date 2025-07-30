from Backend.memory.supabase_client import supabase
from datetime import datetime
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from Backend.graph.states import ProductItem
from typing import Optional , List , Tuple


def serialize_messages(messages: list[BaseMessage]) -> list[dict]:
    return [
        {
            "role": "human" if m.type == "human" else "ai",
            "content": m.content
        }
        for m in messages
    ]

def get_messages(id: int) -> list[BaseMessage]:
    response = supabase.table("summaries").select("messages").eq("id", id).execute()
    data = response.data[0]["messages"] if response.data else None
    if data is None:
        return[]
    return [
        HumanMessage(content=m["content"]) if m["role"] == "human" else AIMessage(content=m["content"])
        for m in data
    ]
def save_messages(id: int, messages: list[BaseMessage]):
    serialized = serialize_messages(messages)
    supabase.table("summaries").upsert({
        "id":id , 
        "messages": serialized , 
        "last_updated": datetime.now().isoformat()
    }).execute()



def get_summary(id: int) -> str:
    res = supabase.table("summaries").select("summary").eq("id", id).execute()
    return res.data[0]["summary"] if res.data else ""


def save_summary(id: int, summary: str):
    supabase.table("summaries").upsert({
        "id": id,
        "summary": summary,
        "last_updated": datetime.now().isoformat()
    }).execute()


def serialize_order(items: List[ProductItem]) -> list[dict]:
    print("Started Serializing Order")
    return [
        {
            "name":item["name"] , 
            "quantity":item["quantity"], 
            "per_unit_price":item["per_unit_price"], 
            "total_price":item["total_price"]
        }
        for item in items
    ]



def get_order(id: int) -> Tuple[List[ProductItem] , Optional[float]]:
    print("Started Get Order")
    order_items = supabase.table("order").select("current_order").eq("id", id).execute()
    items = order_items.data[0]["current_order"] if order_items.data else None
    if items is None:
        return [] , None
    final_price = supabase.table("order").select("final_price").eq("id" , id).execute()
    final_price = final_price.data[0]["final_price"] if final_price.data else None

    return [
        {
            "name": item["name"],
            "quantity": item["quantity"],
            "per_unit_price": item["per_unit_price"],
            "total_price": item["total_price"]
        }
        for item in items] , final_price

    

def save_order(id: int, items: list[ProductItem] = [] , final_price: Optional[float] = None):
    print("Saving Order")
    serialized = serialize_order(items)
    supabase.table("order").upsert({
        "id":id , 
        "current_order": serialized , 
        "final_price":final_price , 
        "last_updated": datetime.now().isoformat()
    }).execute()
