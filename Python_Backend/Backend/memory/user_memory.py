from pydantic import BaseModel, Field
from typing import List, Optional


class UserMemory(BaseModel):
    name: Optional[str] = Field(
        default=None,
        description="The user's preferred name or nickname."
    )
    
    likes: List[str] = Field(
        default_factory=list,
        description="Items or preferences the user likes (e.g., flavors, types of drinks)."
    )

    dislikes: List[str] = Field(
        default_factory=list,
        description="Items or preferences the user dislikes or wants to avoid."
    )

    allergies: List[str] = Field(
        default_factory=list,
        description="Any ingredients or substances the user is allergic to."
    )

    last_order: Optional[str] = Field(
        default=None,
        description="The user's most recent coffee order."
    )

    feedback: List[str] = Field(
        default_factory=list,
        description="General feedback, notes, or suggestions given by the user."
    )

    location: Optional[str] = Field(
        default=None,
        description="The user's city, region, or location (e.g., for delivery or personalization)."
    )