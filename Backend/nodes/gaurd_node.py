from langchain_core.runnables import Runnable
from Backend.agents.guard_agent import GuardAgent
from Backend.graph.states import CoffeeAgentState

class GuardNode(Runnable):
    def __init__(self):
        self.agent = GuardAgent()

    def invoke(self, state: CoffeeAgentState, config=None) -> CoffeeAgentState:
        result = self.agent(state)

        state["decision"] = result["decision"]
        state["response_message"] = result["response_message"]

        return CoffeeAgentState(**state)