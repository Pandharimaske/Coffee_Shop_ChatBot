from langgraph.graph import StateGraph, END , START
from Backend.nodes.gaurd_node import GuardNode
from Backend.nodes.classification_node import ClassificationNode
from Backend.nodes.details_node import DetailsAgentNode
from Backend.nodes.order_node import OrderAgentNode
from Backend.nodes.recommendation_node import RecommendationAgentNode
from Backend.agents.reccomendation_agent import RecommendationAgent

def build_coffee_shop_graph():
    builder = StateGraph(dict)

    # Step 1: Guard agent
    builder.add_node("guard", GuardNode())

    # Step 2: Classification agent
    builder.add_node("classify", ClassificationNode())

    # Step 3: Instantiate and add downstream agents
    builder.add_node("details", DetailsAgentNode())
    builder.add_node("order", OrderAgentNode())

    # ✅ Instantiate the recommendation agent properly
    recommendation_agent = RecommendationAgent(
        apriori_recommendation_path="/Users/pandhari/Desktop/COFFFE_SHOP_CHATBOT/Backend/Data/apriori_recommendations.json",
        popular_recommendation_path="/Users/pandhari/Desktop/COFFFE_SHOP_CHATBOT/Backend/Data/popularity_recommendation.csv"
    )
    builder.add_node("recommend", RecommendationAgentNode(recommendation_agent))

    # Graph flow
    builder.add_edge(START , "guard")

    def guard_decision_router(state):
        return "classify" if state.get("guard_output", {}).get("guard_decision") == "allowed" else "end"

    builder.add_conditional_edges("guard", guard_decision_router, {
        "classify": "classify",
        "end": END
    })

    def classify_router(state):
        return state["classification_output"]["classification_decision"]

    builder.add_conditional_edges("classify", classify_router, {
        "details_agent": "details",
        "order_taking_agent": "order",
        "recommendation_agent": "recommend"
    })

    # Final nodes
    builder.add_edge("details", END)
    builder.add_edge("order", END)
    builder.add_edge("recommend", END)

    return builder.compile()