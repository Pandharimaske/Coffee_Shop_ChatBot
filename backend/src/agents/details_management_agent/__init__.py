"""Details Agent - Handles product and shop information queries."""

from src.agents.details_management_agent.agent import details_management_agent
from src.agents.details_management_agent.prompt import details_prompt
from src.agents.details_management_agent.schema import DetailsResponse

__all__ = [
    "details_management_agent",
    "details_prompt",
    "DetailsResponse",
]
