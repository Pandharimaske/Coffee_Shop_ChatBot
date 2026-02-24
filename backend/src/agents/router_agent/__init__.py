"""Router Agent - Acts as a gatekeeper who routes query to desired agent."""

from src.agents.router_agent.agent import router_agent
from src.agents.router_agent.prompt import router_prompt
from src.agents.router_agent.schema import AgentDecision, AgentType

# Backward compatibility alias
router_node = router_agent

__all__ = [
    "router_agent",
    "router_node",  # Backward compatibility
    "router_prompt",
    "AgentDecision",
    "AgentType",
]
