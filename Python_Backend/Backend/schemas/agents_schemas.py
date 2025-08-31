from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


# ---------------- Enums ---------------- #

class GuardDecisionType(str, Enum):
    allowed = "allowed"
    not_allowed = "not allowed"


class AgentType(str, Enum):
    details_agent = "details_agent"
    order_taking_agent = "order_taking_agent"
    recommendation_agent = "recommendation_agent"
    update_order_agent = "update_order_agent"



class CategoryEnum(str, Enum):
    coffee = "Coffee"
    bakery = "Bakery"
    drinking_chocolate = "Drinking Chocolate"
    flavours = "Flavours"
    general = "General"  # ✅ fallback instead of None/Unknown

class CategoryPrediction(BaseModel):
    category: CategoryEnum = Field(
        ...,
        description=(
            "The main category of the item mentioned by the user. "
            "Must be one of: Coffee, Bakery, Drinking Chocolate, Flavours, General. "
            "Use 'General' if the input does not clearly match any category."
        )
    )

# ---------------- Schemas ---------------- #
class GuardDecision(BaseModel):
    """Schema for guard agent's output determining query access."""
    
    decision: GuardDecisionType = Field(..., description="Decision: allowed or not allowed")

    response_message: Optional[str] = Field(
        default="", 
        description="Message shown to the user. 'Sorry, I can’t help you with that.' if not allowed; empty if allowed."
    )

    memory_node: bool = Field(
        default=False,
        description="Decide whether needs to call long term memory update"
    )


class AgentDecision(BaseModel):
    """Schema for routing the query to the appropriate agent."""
    target_agent: AgentType = Field(..., description="The chosen agent to handle the input")
    response_message: Optional[str] = Field(default="", description="Optional response message to the user")
