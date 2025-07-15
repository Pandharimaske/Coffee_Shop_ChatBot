from pydantic import BaseModel
from typing import Optional, List, Any

class ChatRequest(BaseModel):
    user_input: str
    user_id: int

class ChatResponse(BaseModel):
    response: str