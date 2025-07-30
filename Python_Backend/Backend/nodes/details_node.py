from langchain_core.runnables import Runnable
from Backend.agents.details_agent import DetailsAgent
from Backend.graph.states import CoffeeAgentState

class DetailsAgentNode(Runnable):
    def __init__(self):
        self.agent = DetailsAgent()

    def invoke(self, state: CoffeeAgentState, config=None) -> CoffeeAgentState:
        user_input = state["user_input"]
        if not user_input:
            state["response_message"] = "Sorry, I didn't receive any input."
            return CoffeeAgentState(**state)
        
        response = self.agent.get_response(user_input)
        state["response_message"] = response["response_message"]
        return CoffeeAgentState(**state)
    