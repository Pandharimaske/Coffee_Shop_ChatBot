from langgraph.types import Command
from langgraph.graph import END
from src.graph.state import CoffeeAgentState
from src.utils.util import llm
from src.agents.router_agent.schema import AgentDecision
from src.agents.router_agent.prompt import router_prompt

async def router_agent(state: CoffeeAgentState) -> Command:
    """
    Decides which specialist agent (Details, Order, Recommendation, Update) 
    should handle the user's refined query.
    """

    structured_llm = llm.with_structured_output(AgentDecision)
    chain = router_prompt | structured_llm
    
    try:
        result = await chain.ainvoke({
            "user_input": state.user_input,
            "order": state.order,
            "messages": state.messages,
        })

        result = result.model_dump(mode='json')
        
        return Command(
            update={
                "response_message": result.get('response_message', "")
            },
            goto=result['target_agent']
        )

    except Exception:
        return Command(
            update={
                "response_message": "Sorry, I'm having trouble understanding your request right now. Could you please try again?"
            },
            goto=END,
        )