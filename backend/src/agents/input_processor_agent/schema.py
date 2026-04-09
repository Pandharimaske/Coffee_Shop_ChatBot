from pydantic import BaseModel, Field
from enum import Enum


class ProcessorDecision(str, Enum):
    allowed = "allowed"
    blocked = "blocked"


class InputProcessorResponse(BaseModel):
    """Combined response for guardrail check and query refinement."""
    decision: ProcessorDecision = Field(..., description="Whether the query is allowed or blocked")
    rewritten_input: str = Field(..., description="The self-contained, rewritten query if allowed, or original if blocked")
    response_message: str = Field(default="", description="Friendly redirect message if blocked, empty if allowed")
