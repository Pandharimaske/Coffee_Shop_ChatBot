# App/schemas.py

from pydantic import BaseModel
from typing import Optional, List, Any

class ChatRequest(BaseModel):
    user_input: str
    user_id: int
    state: Optional[dict] = None  # Accept previous state if available

class ChatResponse(BaseModel):
    response: str
    state: dict  # Return the updated state