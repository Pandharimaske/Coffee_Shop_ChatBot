from langchain_core.runnables import Runnable
from Backend.agents.guard_agent import GuardAgent
from Backend.graph.states import CoffeeAgentState
from Backend.utils.memory_manager import get_user_memory
from Backend.utils.summary_memory import get_summary

class GuardNode(Runnable):
    def __init__(self):
        self.agent = GuardAgent()

    def invoke(self, state: CoffeeAgentState, config=None) -> CoffeeAgentState:
        result = self.agent(state)
        return result
        # state["decision"] = result["decision"]
        # state["response_message"] = result["response_message"]
        # state["memory_node"] = result["memory_node"]
        # return CoffeeAgentState(**state)
