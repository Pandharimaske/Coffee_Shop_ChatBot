from langchain_core.runnables import Runnable
from Backend.agents.guard_agent import GuardAgent
from Backend.graph.states import CoffeeAgentState

class GuardNode(Runnable):
    def __init__(self):
        self.agent = GuardAgent()

    def invoke(self, state: CoffeeAgentState, config=None) -> CoffeeAgentState:
        user_input = state["user_input"]
        result = self.agent(user_input)

        state["decision"] = result["decision"]
        state["response_message"] = result["response_message"]

        return CoffeeAgentState(**state)