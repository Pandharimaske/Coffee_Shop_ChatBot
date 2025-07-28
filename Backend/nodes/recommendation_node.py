from langchain_core.runnables import Runnable
from Backend.graph.states import CoffeeAgentState
class RecommendationAgentNode(Runnable):
    def __init__(self, recommendation_agent):
        self.recommendation_agent = recommendation_agent

    def invoke(self, state: CoffeeAgentState, config=None) -> CoffeeAgentState:
        user_input = state.get("user_input" , "")

        return {
                "response_message": "recommendation agent not working please try again later."
            }


        if not user_input:
            return {
                "response_message": "No user message provided to generate a recommendation."
            }

        response = self.recommendation_agent.get_response(user_input)

        return {
            "response_message": response
        }