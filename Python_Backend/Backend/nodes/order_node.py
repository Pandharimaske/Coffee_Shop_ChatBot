from langchain_core.runnables import Runnable
from Backend.agents.order_taking_agent import OrderTakingAgent
from Backend.graph.states import CoffeeAgentState

class OrderAgentNode(Runnable):
    def __init__(self , recommendation_agent):
        self.agent = OrderTakingAgent()
        self.recommendation_agent = recommendation_agent

    def invoke(self, state: CoffeeAgentState, config=None) -> CoffeeAgentState:
        user_input = state["user_input"]
        if not user_input:
            state["response_message"] = "Sorry, I didn’t receive any input."
            return CoffeeAgentState(**state)

        response = self.agent.get_response(user_input)
        available_items = response["available_items"]
        recommendations = self.recommendation_agent.get_apriori_recommendation(products=available_items)

        state["order"] = response["order"]
        state["response_message"] = response["response_message"] + f"Recommendations with this order : {recommendations}"
        state["final_price"] = response["final_price"]

        return CoffeeAgentState(**state)