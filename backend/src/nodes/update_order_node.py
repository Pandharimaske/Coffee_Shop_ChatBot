from langchain_core.runnables import Runnable
from src.agents.order_update import OrderUpdateAgent
from src.graph.states import CoffeeAgentState

class UpdateOrderAgentNode(Runnable):

    def __init__(self):
        self.order_update_agent = OrderUpdateAgent()
    
    def invoke(self, state: CoffeeAgentState, config=None) -> CoffeeAgentState:
        user_input = state.get("user_input")
        if not user_input:
            state["response_message"] = "Sorry, I didn’t receive any input."
            return CoffeeAgentState(**state)

        return self.order_update_agent.update_order(state)
    