# App/chatbot.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from Backend.graph.coffee_shop_graph import build_coffee_shop_graph
from Backend.utils.logger import logger
from Backend.utils.memory_manager import get_user_memory
from Backend.utils.summary_memory import get_summary , get_messages , get_order

graph = build_coffee_shop_graph() 
logger.info("☕ Coffee Shop Bot API initialized")

def get_bot_response(user_input: str, user_id: int) -> dict:
    try:
        state = {
            "user_memory": None,
            "messages" : [] ,
            "chat_summary": "",
            "user_input": "",
            "response_message": None,
            "decision": None,
            "target_agent": None,
            "order": [],
            "final_price": None,
            "memory_node": False,
        }

        state["user_input"] = user_input
        state["user_memory"] = get_user_memory(user_id)
        state["chat_summary"] = get_summary(id=user_id)
        state["messages"] = get_messages(id = user_id)
        state["order"] , state["final_price"] = get_order(id = user_id)

        config = {
            "configurable": {
                "user_id": user_id
            }
        }

        state = graph.invoke(state, config=config)

        return {
            "response": state.get("response_message", "Sorry, I can't help with that."),
            "state": state
        }

    except Exception as e:
        logger.error(f"Graph invocation failed: {e}")
        return {
            "response": "Something went wrong. Please try again later.",
            "state": state or {}
        }