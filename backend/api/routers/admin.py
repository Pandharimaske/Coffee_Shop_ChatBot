from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import logging
from api.auth import CurrentUser
from src.memory.supabase_client import supabase
from src.agents.admin_agent.agent import invoke_admin_agent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])

class AdminChatRequest(BaseModel):
    query: str

def verify_admin(current_user: CurrentUser):
    try:
        res = supabase.table("coffee_shop_profiles").select("is_admin").eq("user_email", current_user.email).execute()
        if not res.data or not res.data[0].get("is_admin"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Error verifying admin status.")
    return current_user

@router.post("/chat")
async def chat_with_admin_agent(req: AdminChatRequest, current_user: CurrentUser):
    verify_admin(current_user)
    
    reply = await invoke_admin_agent(req.query)
    return {"reply": reply}
