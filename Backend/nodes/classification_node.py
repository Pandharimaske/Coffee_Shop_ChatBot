from langchain_core.runnables import Runnable
from Backend.agents.classification_agent import ClassificationAgent
from langgraph.graph import StateGraph, END

class ClassificationNode(Runnable):
    def __init__(self):
        self.agent = ClassificationAgent()

    def invoke(self, state: dict, config=None) -> dict:
        user_input = state.get("input")
        if not user_input:
            raise ValueError("Missing 'input' in state")

        messages = [{"role": "user", "content": user_input}]
        result = self.agent.get_response(messages)

        return {
            "input": user_input,
            "classification_output": {
                "classification_decision": result["classification_output"]["classification_decision"],
                "chain_of_thought": result["classification_output"].get("chain_of_thought", "")
            },
            "classification_message": result["content"]
        }
    
