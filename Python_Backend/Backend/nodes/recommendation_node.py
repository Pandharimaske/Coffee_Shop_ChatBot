from langchain_core.runnables import Runnable
from Backend.graph.states import CoffeeAgentState
class RecommendationAgentNode(Runnable):
    def __init__(self, recommendation_agent):
        self.recommendation_agent = recommendation_agent

    def invoke(self, state: CoffeeAgentState, config=None) -> CoffeeAgentState:
        user_input = state.get("user_input" , "")
        recommendations = self.recommendation_agent.get_popular_recommendation(user_input=user_input) 

        return {"response_message":f"Popular Recommendation: {recommendations}"}