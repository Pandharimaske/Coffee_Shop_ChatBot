"""Guard Agent - Acts as a gatekeeper for the chatbot."""

from src.agents.guard_agent.agent import guard_agent
from src.agents.guard_agent.prompt import guard_prompt
from src.agents.guard_agent.schema import GuardDecision, GuardDecisionType

# Backward compatibility alias
guard_node = guard_agent

__all__ = [
    "guard_agent",
    "guard_node",  # Backward compatibility
    "guard_prompt",
    "GuardDecision",
    "GuardDecisionType",
]
