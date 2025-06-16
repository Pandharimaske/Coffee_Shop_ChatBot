from langchain_core.runnables import Runnable
from Backend.agents.order_taking_agent import OrderTakingAgent
from Backend.graph.states import CoffeeAgentState

class OrderAgentNode(Runnable):
    def __init__(self):
        self.agent = OrderTakingAgent()

    def invoke(self, state: CoffeeAgentState, config=None) -> CoffeeAgentState:
        user_input = state["user_input"]
        if not user_input:
            state["response_message"] = "Sorry, I didn’t receive any input."
            return CoffeeAgentState(**state)

        response = self.agent.get_response(user_input)
        state["response_message"] = response["response_message"]
        state["order"] = response["order"]
        return CoffeeAgentState(**state)
    