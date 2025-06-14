# 📁 Backend/graph/coffee_shop_graph.py

from langgraph.graph import StateGraph, END, START
from Backend.nodes.gaurd_node import GuardNode
from Backend.nodes.classification_node import ClassificationNode
from Backend.nodes.details_node import DetailsAgentNode
from Backend.nodes.order_node import OrderAgentNode
from Backend.nodes.recommendation_node import RecommendationAgentNode
from Backend.agents.reccomendation_agent import RecommendationAgent
from Backend.graph.states import InputState, OutputState, CoffeeAgentState

def build_coffee_shop_graph():
    # ✅ Use structured state
    builder = StateGraph(CoffeeAgentState, input=InputState, output=OutputState)

    # Step 1: Guard agent
    builder.add_node("guard", GuardNode())

    # Step 2: Classification agent
    builder.add_node("classify", ClassificationNode())

    # Step 3: Downstream agent nodes
    builder.add_node("details", DetailsAgentNode())
    builder.add_node("order_taking", OrderAgentNode())

    recommendation_agent = RecommendationAgent(
        apriori_recommendation_path="/Users/pandhari/Coffee_Shop_ChatBot/Backend/Data/apriori_recommendations.json",
        popular_recommendation_path="/Users/pandhari/Coffee_Shop_ChatBot/Backend/Data/popularity_recommendation.csv"
    )
    builder.add_node("recommend", RecommendationAgentNode(recommendation_agent))

    # Entry
    builder.set_entry_point("guard")

    # Decision router after guard
    def guard_decision_router(state: CoffeeAgentState):
        return "classify" if state.get("decision") == "allowed" else "end"

    builder.add_conditional_edges("guard", guard_decision_router, {
        "classify": "classify",
        "end": END
    })

    # Decision router after classification
    def classify_router(state: CoffeeAgentState):
        return state["target_agent"]

    builder.add_conditional_edges("classify", classify_router, {
        "details_agent": "details",
        "order_taking_agent": "order_taking",
        "recommendation_agent": "recommend"
    })

    # Final responses
    builder.add_edge("details", END)
    builder.add_edge("order_taking", END)
    builder.add_edge("recommend", END)

    return builder.compile()