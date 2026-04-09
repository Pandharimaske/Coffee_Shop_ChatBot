import logging
from langgraph.types import Command
from langgraph.graph import END

from src.utils.util import small_llm
from src.agents.input_processor_agent.schema import InputProcessorResponse
from src.agents.input_processor_agent.prompt import input_processor_prompt
from src.graph.state import CoffeeAgentState

logger = logging.getLogger(__name__)

_chain = input_processor_prompt | small_llm.with_structured_output(InputProcessorResponse)


async def input_processor_agent(state: CoffeeAgentState) -> Command:
    """
    Unified agent for gatekeeping (Guard) and query refinement (Intent Refiner).
    Runs first to ensure the request is valid and self-contained.
    """
    user_input = state.user_input

    if not user_input.strip():
        return Command(
            update={"response_message": "I didn't catch that — what can I get you?"},
            goto=END
        )

    try:
        # Format context for the LLM
        recent_messages = state.messages[-6:] if state.messages else []
        formatted_messages = "\n".join([
            f"{getattr(m, 'type', 'unknown').upper()}: {m.content}"
            for m in recent_messages
        ]) or "(no prior messages)"

        result: InputProcessorResponse = await _chain.ainvoke({
            "user_input": user_input,
            "messages": formatted_messages,
            "user_memory": state.user_memory.model_dump(),
            "order": [f"{i.name} x{i.quantity}" for i in state.order] or "empty",
        })

        if result.decision == "blocked":
            logger.info(f"Input Processor: BLOCKED — {result.response_message[:40]}")
            return Command(
                update={"response_message": result.response_message},
                goto=END
            )

        logger.info(f"Input Processor: ALLOWED — Rewritten: {result.rewritten_input[:40]}")
        return Command(
            update={
                "user_input": result.rewritten_input,
                "response_message": ""
            },
            goto="memory"
        )

    except Exception as e:
        logger.error(f"input_processor_agent failed: {e}", exc_info=True)
        
        # Check for specific LLM API errors
        from src.utils.util import get_llm_error_message
        if api_msg := get_llm_error_message(e):
            return Command(
                update={"response_message": api_msg},
                goto=END
            )

        # Generic Fallback: Allow but don't rewrite
        return Command(goto="memory")
