from langchain_core.runnables import Runnable
from Backend.agents.classification_agent import ClassificationAgent
from Backend.graph.states import CoffeeAgentState

class ClassificationNode(Runnable):
    def __init__(self):
        self.agent = ClassificationAgent()

    def invoke(self, state: CoffeeAgentState, config=None) -> CoffeeAgentState:
        user_input = state.get("user_input")
        if not user_input:
            raise ValueError("Missing 'user_input' in state")
        
        # Pass the entire state to the agent
        result = self.agent.get_response(user_input, state)

        # Update state with classification results
        state["target_agent"] = result["target_agent"]
        state["response_message"] = result["response_message"]

        return state  # Return updated state directly