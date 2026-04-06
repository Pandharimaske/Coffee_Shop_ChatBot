"""Memory Agent - Extracts and persists user preferences from conversation."""

import logging
from langgraph.types import Command, interrupt
from langgraph.errors import GraphInterrupt
from langchain_core.runnables import RunnableConfig

from src.utils.util import small_llm
from src.graph.state import CoffeeAgentState
from src.memory.memory_manager import (
    save_user_memory,
    merge_and_update_memory,
    remove_from_memory,
    replace_in_memory,
)
from src.agents.memory_management_agent.prompt import memory_extraction_prompt
from src.agents.memory_management_agent.schema import MemoryIntent

logger = logging.getLogger(__name__)

_extractor = memory_extraction_prompt | small_llm.with_structured_output(MemoryIntent)


async def memory_agent(state: CoffeeAgentState, config: RunnableConfig) -> Command:
    """
    Runs after guard, before intent_refiner.

    - Extracts memory preferences from user input
    - Saves to Supabase if anything found
    - Always routes to intent_refiner — router decides if general_agent should acknowledge
    """
    user_id: str = config.get("configurable", {}).get("user_id", "anonymous")

    try:
        intent: MemoryIntent = await _extractor.ainvoke({
            "user_input": state.user_input,
            "user_memory": state.user_memory.model_dump(),
            "chat_summary": state.chat_summary,
        })

        if not intent.has_updates():
            return Command(goto="intent_refiner")

        # Trigger HITL before applying
        status = interrupt({
            "action": "memory_validation",
            "details": intent.model_dump()
        })

        if status == "reject":
            logger.info("User rejected memory update via HITL.")
            return Command(goto="intent_refiner")

        # Apply updates
        memory = state.user_memory.model_copy(deep=True)

        logger.info(f"--- MEMORY AGENT: APPLYING UPDATES for {user_id} ---")
        logger.info(f"Current Memory: {memory.model_dump()}")
        logger.info(f"Intent (Remove): {intent.remove}")
        logger.info(f"Intent (Add): {intent.add_or_update}")

        if intent.add_or_update:
            memory = merge_and_update_memory(intent.add_or_update, memory)
        if intent.remove:
            memory = remove_from_memory(intent.remove, memory)
        if intent.replace:
            memory = replace_in_memory(intent.replace, memory)

        logger.info(f"Updated Memory (Ready to Save): {memory.model_dump()}")

        # Persist to Supabase
        if user_id != "anonymous":
            save_user_memory(user_id, memory)
        else:
            logger.debug("Skipping Supabase save — no user_id in config")

        # Always forward to intent_refiner with updated memory
        # Router will send to general_agent if the message was memory-only
        return Command(
            update={"user_memory": memory},
            goto="intent_refiner"
        )

    except GraphInterrupt:
        # Pass LangGraph standard interrupt up
        raise
    except Exception as e:
        logger.error(f"memory_agent failed: {e}", exc_info=True)
        return Command(goto="intent_refiner")
