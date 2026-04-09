from langgraph.types import Command
from langgraph.graph import END
from src.graph.state import CoffeeAgentState
from src.utils.util import small_llm
from src.agents.router_agent.schema import AgentDecision
from src.agents.router_agent.prompt import router_prompt

async def router_agent(state: CoffeeAgentState) -> Command:
    """
    Decides which specialist agent (Details, Order, Recommendation, Update) 
    should handle the user's refined query.
    """

    structured_llm = small_llm.with_structured_output(AgentDecision)
    chain = router_prompt | structured_llm
    
    try:
        # Strip to clean role:content pairs — avoid leaking metadata/tool_calls into the prompt
        def _fmt(m) -> str:
            role = "user" if m.__class__.__name__ == "HumanMessage" else "assistant"
            content = m.content if isinstance(m.content, str) else str(m.content)
            return f"{role}: {content}"

        recent = state.messages[-6:]  # last 3 turns is enough context for routing
        formatted_messages = "\n".join(_fmt(m) for m in recent) or "(no prior messages)"

        result = await chain.ainvoke({
            "user_input": state.user_input,
            "order": [f"{i.name} x{i.quantity}" for i in state.order] or "empty",
            "messages": formatted_messages,
        })

        result = result.model_dump(mode='json')
        
        return Command(
            update={
                "response_message": result.get('response_message', "")
            },
            goto=result['target_agent']
        )

    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"router_agent failed: {e}", exc_info=True)
        
        # Check for specific LLM API errors
        from src.utils.util import get_llm_error_message
        msg = get_llm_error_message(e) or "Sorry, I'm having trouble understanding your request right now. Could you please try again?"
        
        return Command(
            update={
                "response_message": msg
            },
            goto=END,
        )