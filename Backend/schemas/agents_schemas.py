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


class RecommendationTypeEnum(str, Enum):
    apriori = "apriori"
    popular = "popular"
    popular_by_category = "popular by category"


# ---------------- Schemas ---------------- #
class GuardDecision(BaseModel):
    """Schema for guard agent's output determining query access."""
    decision: GuardDecisionType = Field(..., description="Decision: allowed or not allowed")
    response_message: Optional[str] = Field(
        default="", 
        description="Message shown to the user. 'Sorry, I can’t help you with that.' if not allowed; empty if allowed."
    )


class AgentDecision(BaseModel):
    """Schema for routing the query to the appropriate agent."""
    target_agent: AgentType = Field(..., description="The chosen agent to handle the input")
    response_message: Optional[str] = Field(default="", description="Optional response message to the user")


class RecommendationType(BaseModel):
    """Schema defining the type and parameters of product recommendation."""
    recommendation_type: RecommendationTypeEnum = Field(
        ..., description="Type of recommendation"
    )
    parameters: List[str] = Field(description="List of items or categories for recommendations")
