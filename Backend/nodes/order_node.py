from langchain_core.runnables import Runnable
from Backend.agents.order_taking import OrderTakingAgent

class OrderAgentNode(Runnable):
    def __init__(self):
        self.agent = OrderTakingAgent()

    def invoke(self, state: dict, config=None) -> dict:
        user_input = state.get("input", "")
        if not user_input:
            return {
                "input": user_input,
                "agent": "order_taking_agent",
                "content": "Sorry, I didn’t receive any input."
            }

        response = self.agent.get_response(user_input)
        return {
            "input": user_input,
            "agent": "order_taking_agent",
            "content": response["content"]
        }
    