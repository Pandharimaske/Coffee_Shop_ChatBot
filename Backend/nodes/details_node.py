from langchain_core.runnables import Runnable
from Backend.agents.details_agent import DetailsAgent  # Ensure this path matches your structure

class DetailsAgentNode(Runnable):
    def __init__(self):
        self.agent = DetailsAgent()

    def invoke(self, state: dict, config=None) -> dict:
        user_input = state.get("input", "")
        if not user_input:
            return {
                "input": user_input,
                "agent": "details_agent",
                "content": "Sorry, I didn't receive any input."
            }

        response = self.agent.get_response(user_input)
        return {
            "input": user_input,
            "agent": "details_agent",
            "content": response["content"]
        }