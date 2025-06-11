from langchain_core.runnables import Runnable

class OrderAgentNode(Runnable):
    def invoke(self, state: dict, config=None) -> dict:
        return {
            "input": state.get("input"),
            "agent": "order_taking_agent",
            "content": "This is a placeholder response from the Order Agent."
        }