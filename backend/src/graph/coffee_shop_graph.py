# 📁 Backend/graph/coffee_shop_graph.py
from langgraph.graph import StateGraph, END, START
from src.nodes.gaurd_node import GuardNode
from src.nodes.classification_node import ClassificationNode
from src.nodes.details_node import DetailsAgentNode
from src.nodes.order_node import OrderAgentNode
from src.nodes.recommendation_node import RecommendationAgentNode
from src.agents.reccomendation_agent import RecommendationAgent
from src.nodes.update_order_node import UpdateOrderAgentNode
# from Backend.nodes.response_node import ResponseNode
from src.nodes.memory_node import MemoryNode
from src.nodes.chat_summary_node import SummaryNode
from src.nodes.query_rewrite_node import QueryRewriterNode
from src.graph.states import CoffeeAgentState



def build_coffee_shop_graph():
    # ✅ Use structured state
    builder = StateGraph(CoffeeAgentState, input=CoffeeAgentState, output=CoffeeAgentState)
    
    recommendation_agent = RecommendationAgent(
        apriori_recommendation_path="Backend/Data/apriori_recommendations.json",
        popular_recommendation_path="Backend/Data/popularity_recommendation.csv"
    )

    # Nodes
    builder.add_node("guard", GuardNode())
    builder.add_node("memory", MemoryNode())
    builder.add_node("classify", ClassificationNode())
    builder.add_node("details", DetailsAgentNode())
    builder.add_node("take_order", OrderAgentNode(recommendation_agent))
    builder.add_node("update_order", UpdateOrderAgentNode())
    # builder.add_node("final_response", ResponseNode())
    builder.add_node("chat_summary", SummaryNode())
    builder.add_node("query_rewrite", QueryRewriterNode())
    builder.add_node("recommend", RecommendationAgentNode(recommendation_agent))

    # Entry
    builder.add_edge(START , "query_rewrite")

    builder.add_edge("query_rewrite" , "guard")

    builder.add_edge("guard" , "memory")

    # Step 2: Route memory/skip_memory to classify or final_response
    def post_memory_router(state: CoffeeAgentState):
        return "classify" if state.get("decision") == "allowed" else "chat_summary"

    builder.add_conditional_edges("memory", post_memory_router, {
        "classify": "classify",
        "chat_summary": "chat_summary"
    })

    # Step 3: Classification routing
    def classify_router(state: CoffeeAgentState):
        return state["target_agent"]

    builder.add_conditional_edges("classify", classify_router, {
        "details_agent": "details",
        "order_taking_agent": "take_order",
        "recommendation_agent": "recommend",
        "update_order_agent": "update_order"
    })

    # Step 4: Agent responses to final
    builder.add_edge("details", "chat_summary")
    builder.add_edge("take_order", "chat_summary")
    builder.add_edge("recommend", "chat_summary")
    builder.add_edge("update_order", "chat_summary")
    # builder.add_edge("final_response" , "chat_summary")
    builder.add_edge("chat_summary", END)

    return builder.compile()