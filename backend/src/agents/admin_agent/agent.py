import logging
import os
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.utilities import SQLDatabase
from src.utils.util import llm

logger = logging.getLogger(__name__)

db_url = os.getenv("SUPABASE_DB_URL")
try:
    db = SQLDatabase.from_uri(db_url) if db_url else None
except Exception as e:
    logger.error(f"Failed to connect SQLDatabase: {e}")
    db = None

system_prompt = """You are an elite Business Intelligence AI for Merry's Way Coffee Shop.
You have direct read-only access to our PostgreSQL database via SQL tools. Your job is to answer the shop owner's questions accurately by writing SQL.

Database Context:
- 'coffee_shop_profiles' contains user data.
- 'coffee_shop_orders' contains active/past orders (items jsonb, total float).
- 'coffee_shop_products' contains menu inventory.

Output formatting:
1. Simply answer questions naturally. If the user requests lists, use clean Markdown tables.
2. If the user explicitly asks you to "plot", "graph", or "chart", you MUST output an exact JSON block formatted inside a markdown fence:
```json
{
  "type": "recharts_bar", 
  "data": [{"name": "Latte", "value": 500}, {"name": "Mocha", "value": 200}],
  "xKey": "name",
  "yKey": "value"
}
```
Supported types: "recharts_bar", "recharts_line".
"""

_agent_executor = None

def get_admin_agent():
    global _agent_executor
    if _agent_executor is not None:
        return _agent_executor

    if not db:
        raise ValueError("SUPABASE_DB_URL is missing. SQL agent cannot start.")
    
    _agent_executor = create_sql_agent(
        llm=llm,
        db=db,
        agent_type="openai-tools",
        top_k=50,
        verbose=True,
    )
    return _agent_executor

async def invoke_admin_agent(query: str) -> str:
    agent = get_admin_agent()
    try:
        prompt = f"{system_prompt}\n\nOwner Request: {query}"
        res = await agent.ainvoke({"input": prompt})
        return res["output"]
    except Exception as e:
        logger.error(f"Admin SQL Agent failed: {str(e)}", exc_info=True)
        return f"Sorry, I encountered an error querying the database: {str(e)}"
