from pydantic import BaseModel, Field
from typing import List, Optional


class UserMemory(BaseModel):
    name: Optional[str] = Field(default=None, description="The user's preferred name or nickname.")
    likes: List[str] = Field(default_factory=list, description="Items or preferences the user likes.")
    dislikes: List[str] = Field(default_factory=list, description="Items or preferences the user dislikes.")
    allergies: List[str] = Field(default_factory=list, description="Ingredients the user is allergic to.")
    last_order: Optional[str] = Field(default=None, description="The user's most recent order.")
    feedback: List[str] = Field(default_factory=list, description="General feedback or notes from the user.")
    location: Optional[str] = Field(default=None, description="The user's city or region.")
