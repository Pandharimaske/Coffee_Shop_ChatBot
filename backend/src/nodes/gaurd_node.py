from langchain_core.runnables import Runnable
from src.agents.guard_agent import GuardAgent
from src.graph.states import CoffeeAgentState
from src.utils.memory_manager import get_user_memory
from src.utils.summary_memory import get_summary

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
