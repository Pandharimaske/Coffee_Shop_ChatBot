"""Recommendation Agent - Personalized product recommendations using user memory + RAG."""

import logging
from datetime import datetime
from langchain_core.messages import AIMessage
from langgraph.types import Command
from langgraph.graph import END

from src.utils.util import llm
from src.graph.state import CoffeeAgentState
from src.rag.retriever import search_products
from src.agents.recommendation_management_agent.prompt import recommendation_prompt

logger = logging.getLogger(__name__)

_chain = recommendation_prompt | llm


def _build_search_query(user_input: str, memory) -> str:
    """Build a smart search query using user input + preferences."""
    parts = [user_input]
    if memory.likes:
        parts.append(" ".join(memory.likes[:3]))
    # Add time-of-day context
    hour = datetime.now().hour
    if hour < 11:
        parts.append("morning coffee")
    elif hour < 15:
        parts.append("lunch")
    elif hour < 18:
        parts.append("afternoon")
    else:
        parts.append("evening")
    return " ".join(parts)


def _format_products(products: list) -> str:
    if not products:
        return "No specific products found — recommend from general knowledge."
    lines = []
    for p in products:
        meta = p.get("metadata", {})
        name = meta.get("name") or p.get("name", "Unknown")
        price = meta.get("price") or p.get("price", "?")
        category = meta.get("category", "")
        desc = meta.get("description", "")
        lines.append(f"- {name} (₹{price}) [{category}]{': ' + desc if desc else ''}")
    return "\n".join(lines)


async def recommendation_management_agent(state: CoffeeAgentState) -> Command:
    try:
        memory = state.user_memory

        # Build search query based on user input + preferences
        query = _build_search_query(state.user_input, memory)

        # Fetch relevant products from Pinecone
        products = search_products(query, top_k=6)

        # Filter out allergies from candidates
        if memory.allergies:
            allergens = {a.lower() for a in memory.allergies}
            products = [
                p for p in products
                if not any(
                    allergen in str(p.get("metadata", {}).get("ingredients", "")).lower()
                    for allergen in allergens
                )
            ]

        response = await _chain.ainvoke({
            "user_input": state.user_input,
            "likes": memory.likes or "no preferences noted",
            "dislikes": memory.dislikes or "none",
            "allergies": memory.allergies or "none",
            "last_order": memory.last_order or "no previous order",
            "products": _format_products(products),
        })

        msg = response.content
        return Command(
            update={
                "response_message": msg,
                "messages": [AIMessage(content=msg)],
            },
            goto=END
        )

    except Exception as e:
        logger.error(f"recommendation_management_agent failed: {e}", exc_info=True)
        msg = "I'd love to recommend something! Could you tell me what kind of mood you're in — something sweet, strong, light, or a snack?"
        return Command(
            update={"response_message": msg, "messages": [AIMessage(content=msg)]},
            goto=END
        )
