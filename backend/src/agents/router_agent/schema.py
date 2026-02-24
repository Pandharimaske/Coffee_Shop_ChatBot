from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class AgentType(str, Enum):
    details_management_agent = "details_management_agent"
    order_management_agent = "order_management_agent"
    recommendation_management_agent = "recommendation_management_agent"
    general_agent = "general_agent"



class AgentDecision(BaseModel):
    """Schema for routing the query to the appropriate agent."""
    target_agent: AgentType = Field(..., description="The chosen agent to handle the input")
    response_message: Optional[str] = Field(default="", description="Optional response message to the user")