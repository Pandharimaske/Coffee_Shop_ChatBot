from langgraph.graph import StateGraph, START, END
from src.agents.guard_agent import guard_agent
from src.agents.memory_management_agent import memory_agent
from src.agents.intent_refiner_agent import intent_refiner_agent
from src.agents.router_agent import router_agent
from src.agents.details_management_agent import details_management_agent
from src.agents.order_management_agent import order_management_agent
from src.agents.general_agent import general_agent
from src.agents.recommendation_management_agent import recommendation_management_agent

from src.graph.state import CoffeeAgentState


def build_coffee_shop_graph():
    builder = StateGraph(CoffeeAgentState)

    builder.add_node("guard", guard_agent)
    builder.add_node("memory", memory_agent)
    builder.add_node("intent_refiner", intent_refiner_agent)
    builder.add_node("router", router_agent)
    builder.add_node("details_management_agent", details_management_agent)
    builder.add_node("order_management_agent", order_management_agent)
    builder.add_node("recommendation_management_agent", recommendation_management_agent)
    builder.add_node("general_agent", general_agent)

    builder.add_edge(START, "guard")
    builder.add_edge("intent_refiner", "router")

    return builder.compile()
