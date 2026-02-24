"""Prompt templates for the chatbot."""

from src.prompts.router_prompt import router_prompt
from src.prompts.response_prompt import response_prompt
from src.prompts.memory_prompts import memory_prompts

# Agent-specific prompts (now in agent folders)
from src.agents.guard_agent import guard_prompt
from src.agents.intent_refiner_agent import intent_refiner_prompt
from src.agents.order_management_agent import order_management_prompt
from src.agents.details_management_agent import details_prompt
from src.agents.recommendation_agent import recommendation_prompt

__all__ = [
    "router_prompt",
    "response_prompt",
    "memory_prompts",
    # Agent-specific prompts
    "guard_prompt",
    "intent_refiner_prompt",
    "order_management_prompt",
    "details_prompt",
    "recommendation_prompt",
]
