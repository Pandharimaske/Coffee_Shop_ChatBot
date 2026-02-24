"""Intent Refiner Agent - Resolves context in user queries."""

import logging
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage
from langgraph.types import Command
from langgraph.graph import END

from src.graph.state import CoffeeAgentState
from src.utils.util import llm
from src.agents.intent_refiner_agent.prompt import intent_refiner_prompt

logger = logging.getLogger(__name__)


async def intent_refiner_agent(state: CoffeeAgentState):
    """
    Refines the user query by resolving context (e.g., 'it', 'the usual').
    
    Uses chat history and user memory to make references explicit.
    
    Args:
        state: Current conversation state
        
    Returns:
        Command with refined user_input
    """
    chain = intent_refiner_prompt | llm | StrOutputParser()

    try:
        # Invoke the refiner
        refined_query = await chain.ainvoke({
            "user_input": state.user_input,
            "messages": state.messages,
            "chat_summary": state.chat_summary,
            "user_memory": str(state.user_memory),
        })

        refined = refined_query.strip()
        logger.debug(f"Intent refined: '{state.user_input}' -> '{refined}'")

        return Command(
            update={
                "user_input": refined,
                "messages": [HumanMessage(content=refined)],
            },
            goto="router"
        )

    except Exception as e:
        logger.exception(f"Intent refiner failed: {e}")
        return Command(
            update={
                "response_message": "I'm having a bit of trouble understanding that. Could you try rephrasing your coffee request?"
            },
            goto=END
        )


# Backward compatibility alias
intent_refiner_node = intent_refiner_agent
