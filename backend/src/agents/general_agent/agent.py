"""General Agent - Handles greetings, small talk, memory acknowledgements, order status and fallback."""

import logging
from langchain_core.messages import AIMessage
from langgraph.types import Command
from langgraph.graph import END

from src.utils.util import llm
from src.agents.general_agent.prompt import general_prompt
from src.graph.state import CoffeeAgentState

logger = logging.getLogger(__name__)

_chain = general_prompt | llm


async def general_agent(state: CoffeeAgentState) -> Command:
    try:
        # Format order for prompt — full details
        if state.order:
            order_lines = [
                f"  • {item.name} x{item.quantity} @ ₹{item.per_unit_price:.2f} = ₹{item.total_price:.2f}"
                for item in state.order
            ]
            current_order = "\n" + "\n".join(order_lines)
            order_total = f"{state.final_price:.2f}"
        else:
            current_order = "empty"
            order_total = "0.00"

        response = await _chain.ainvoke({
            "messages": state.messages,
            "user_memory": state.user_memory.model_dump(),
            "current_order": current_order,
            "order_total": order_total,
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
        logger.error(f"general_agent failed: {e}", exc_info=True)
        msg = "Hey there! Sorry, I had a small hiccup. How can I help you today?"
        return Command(
            update={"response_message": msg, "messages": [AIMessage(content=msg)]},
            goto=END
        )
