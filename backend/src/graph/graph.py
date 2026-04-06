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
import os

_checkpointer = None

def _get_checkpointer():
    """Use PostgresSaver in production (Linux), MemorySaver on macOS dev.
    psycopg's C extension segfaults on macOS ARM when forked by uvicorn.
    """
    global _checkpointer
    if _checkpointer is not None:
        return _checkpointer

    import platform
    is_mac = platform.system() == "Darwin"
    db_uri = os.getenv("SUPABASE_DB_URL")

    if is_mac or not db_uri:
        # macOS dev: psycopg segfaults, use in-memory
        from langgraph.checkpoint.memory import MemorySaver
        _checkpointer = MemorySaver()
        return _checkpointer

    # Production (Linux): use persistent Postgres checkpointer
    try:
        from psycopg_pool import ConnectionPool
        from langgraph.checkpoint.postgres import PostgresSaver
        pool = ConnectionPool(
            conninfo=db_uri,
            max_size=20,
            open=True,
            kwargs={"autocommit": True, "prepare_threshold": 0}
        )
        saver = PostgresSaver(pool)
        saver.setup()
        _checkpointer = saver
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Postgres checkpointer failed, falling back to MemorySaver: {e}")
        from langgraph.checkpoint.memory import MemorySaver
        _checkpointer = MemorySaver()

    return _checkpointer


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

    return builder.compile(checkpointer=_get_checkpointer())
