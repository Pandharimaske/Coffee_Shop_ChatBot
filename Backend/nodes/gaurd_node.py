from langgraph.graph import StateGraph, END
from langchain_core.runnables import Runnable
from Backend.agents.guard_agent import GuardAgent

class GuardNode(Runnable):
    def __init__(self):
        self.agent = GuardAgent()

    def invoke(self, state: dict, config=None) -> dict:
        user_input = state.get("input")
        if not user_input:
            raise ValueError("Missing 'input' in state")

        result = self.agent.get_response(user_input)

        return {
        "input": user_input,
        "guard_output": {
            "guard_decision": result["guard_output"]["guard_decision"],
            "chain_of_thought": result["guard_output"]["chain_of_thought"]
        },
        "guard_message": result["content"]
    }