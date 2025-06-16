from Backend.graph.coffee_shop_graph import build_coffee_shop_graph
from Backend.utils.logger import logger

# Build the graph only once on startup
graph = build_coffee_shop_graph()
logger.info("☕ Coffee Shop Bot API initialized")

def get_bot_response(user_message: str) -> str:
    try:
        result = graph.invoke({"user_input": user_message})
        return result.get("response_message", "Sorry, I can't help with that.")
    except Exception as e:
        logger.error(f"Graph invocation failed: {e}")
        return "Something went wrong. Please try again later."