from langgraph.graph import StateGraph, START, END
from src.agents.input_processor_agent import input_processor_agent
from src.agents.memory_management_agent import memory_agent
from src.agents.router_agent import router_agent
from src.agents.details_management_agent import details_management_agent
from src.agents.order_management_agent import order_management_agent
from src.agents.general_agent import general_agent
from src.agents.recommendation_management_agent import recommendation_management_agent

from src.graph.state import CoffeeAgentState
import os

_checkpointer = None

def _get_checkpointer():
    """
    Checkpointer strategy:
    - macOS dev  → SqliteSaver (file-backed, survives --reload, no psycopg issues)
    - Linux/prod → PostgresSaver via connection pool (Supabase Transaction Pooler)
    - Fallback   → MemorySaver (last resort, resets on restart)

    psycopg's C extension segfaults on macOS ARM when forked by uvicorn's
    multiprocessing — that's why we avoid PostgresSaver on Darwin entirely.
    """
    global _checkpointer
    if _checkpointer is not None:
        return _checkpointer

    import platform
    import logging
    log = logging.getLogger(__name__)

    is_mac = platform.system() == "Darwin"
    db_uri = os.getenv("SUPABASE_DB_URL")

    if is_mac or not db_uri:
        # macOS dev: use SQLite so checkpoints survive --reload
        try:
            from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
            _checkpointer = AsyncSqliteSaver.from_conn_string("./dev_checkpoints.db")
            log.info("SqliteSaver checkpointer initialised (dev_checkpoints.db)")
        except Exception as e:
            log.warning(f"SqliteSaver unavailable ({e}), falling back to MemorySaver")
            from langgraph.checkpoint.memory import MemorySaver
            _checkpointer = MemorySaver()
        return _checkpointer

    # Production (Linux): use persistent Postgres checkpointer
    try:
        from psycopg_pool import ConnectionPool
        from langgraph.checkpoint.postgres import PostgresSaver

        # Supabase Transaction Pooler (Port 6543) — requires prepare_threshold=0
        separator = "&" if "?" in db_uri else "?"
        full_uri = f"{db_uri}{separator}sslmode=require&tcp_user_timeout=10000"

        pool = ConnectionPool(
            conninfo=full_uri,
            max_size=10,
            open=True,
            kwargs={"autocommit": True, "prepare_threshold": 0},
        )
        saver = PostgresSaver(pool)
        saver.setup()
        _checkpointer = saver
        log.info("PostgresSaver checkpointer initialised via Supabase Transaction Pooler")
    except Exception as e:
        log.warning(f"PostgresSaver failed, falling back to MemorySaver: {e}")
        from langgraph.checkpoint.memory import MemorySaver
        _checkpointer = MemorySaver()

    return _checkpointer



def build_coffee_shop_graph():
    builder = StateGraph(CoffeeAgentState)

    builder.add_node("input_processor", input_processor_agent)
    builder.add_node("memory", memory_agent)
    builder.add_node("router", router_agent)
    builder.add_node("details_management_agent", details_management_agent)
    builder.add_node("order_management_agent", order_management_agent)
    builder.add_node("recommendation_management_agent", recommendation_management_agent)
    builder.add_node("general_agent", general_agent)

    builder.add_edge(START, "input_processor")
    builder.add_edge("memory", "router")

    return builder.compile(checkpointer=_get_checkpointer())
