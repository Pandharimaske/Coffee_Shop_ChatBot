from pydantic import BaseModel, Field
from enum import Enum


class GuardDecisionType(str, Enum):
    allowed = "allowed"
    not_allowed = "not allowed"


class GuardDecision(BaseModel):
    decision: GuardDecisionType = Field(
        ...,
        description="Whether to allow or block this query"
    )
    response_message: str = Field(
        default="",
        description="Empty if allowed. Friendly redirect message if not allowed."
    )
