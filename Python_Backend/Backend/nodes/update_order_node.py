from langchain_core.runnables import Runnable
from Backend.agents.order_update import update_order
from Backend.graph.states import CoffeeAgentState

class UpdateOrderAgentNode(Runnable):
    def invoke(self, state: CoffeeAgentState, config=None) -> CoffeeAgentState:
        user_input = state.get("user_input")
        if not user_input:
            state["response_message"] = "Sorry, I didn’t receive any input."
            return CoffeeAgentState(**state)

        return update_order(state)
    