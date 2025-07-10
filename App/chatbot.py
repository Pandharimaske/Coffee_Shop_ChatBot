# App/chatbot.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from Backend.graph.coffee_shop_graph import build_coffee_shop_graph
from Backend.utils.logger import logger

graph = build_coffee_shop_graph() 
logger.info("☕ Coffee Shop Bot API initialized")

def get_bot_response(user_message: str, user_id: int, state: dict = None) -> dict:
    try:
        current_state = state or {
            "user_memory": None,
            "chat_summary": "",
            "user_input": "",
            "response_message": None,
            "decision": None,
            "target_agent": None,
            "order": [],
            "final_price": None,
            "memory_node": False,
        }

        current_state["user_input"] = user_message

        config = {
            "configurable": {
                "user_id": user_id
            }
        }

        result_state = graph.invoke(current_state, config=config)

        return {
            "response": result_state.get("response_message", "Sorry, I can't help with that."),
            "state": result_state
        }

    except Exception as e:
        logger.error(f"Graph invocation failed: {e}")
        return {
            "response": "Something went wrong. Please try again later.",
            "state": state or {}
        }