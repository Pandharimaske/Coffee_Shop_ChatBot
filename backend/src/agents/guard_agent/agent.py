"""Guard Agent - Gatekeeper for the chatbot."""

import logging
from langgraph.types import Command
from langgraph.graph import END

from src.utils.util import llm
from src.agents.guard_agent.schema import GuardDecision
from src.agents.guard_agent.prompt import guard_prompt
from src.graph.state import CoffeeAgentState

logger = logging.getLogger(__name__)

_chain = guard_prompt | llm.with_structured_output(GuardDecision)


async def guard_agent(state: CoffeeAgentState) -> Command:
    """
    Validates user input. Allows coffee-related queries through,
    blocks everything else with a friendly redirect.
    Always routes allowed messages to memory agent.
    """
    user_input = state.user_input

    if not user_input.strip():
        return Command(
            update={"response_message": "I didn't catch that — what can I get you?"},
            goto=END
        )

    try:
        recent_messages = state.messages[-4:] if state.messages else []
        context = {
            "recent_messages": [
                f"{getattr(m, 'type', 'unknown').upper()}: {m.content}"
                for m in recent_messages
            ],
            "order": [i.model_dump() for i in state.order],
        }

        result: GuardDecision = await _chain.ainvoke({
            "user_input": user_input,
            "state": str(context),
        })

        if result.decision == "allowed":
            logger.info(f"Guard: allowed — routing to memory")
            return Command(goto="memory")
        else:
            logger.info(f"Guard: blocked — {result.response_message[:40]}")
            return Command(
                update={"response_message": result.response_message},
                goto=END
            )

    except Exception as e:
        logger.error(f"guard_agent failed: {e}", exc_info=True)
        return Command(
            update={"response_message": "I'm having a little trouble. Can we stick to coffee orders for now?"},
            goto=END
        )
