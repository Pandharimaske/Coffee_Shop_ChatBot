"""General Agent - Handles greetings, small talk, and fallback conversations."""

from src.agents.general_agent.agent import general_agent
from src.agents.general_agent.prompt import general_prompt

__all__ = [
    "general_agent",
    "general_prompt",
]
