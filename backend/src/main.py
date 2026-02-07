from src.graph.coffee_shop_graph import build_coffee_shop_graph
from src.graph.states import CoffeeAgentState
from src.utils.logger import logger


# ------------------ Config -------------------
config = {
    "configurable": {
        "user_id": 10
    }
}
# ------------------ Run CLI Bot -------------------
def main():
    graph = build_coffee_shop_graph()
    logger.info("Coffee Shop Bot initialized")

    print("☕ Welcome to the Coffee Shop Bot! Ask anything or type 'exit' to quit.")
    state = CoffeeAgentState(
        user_memory = None,
        messages = [] , 
        chat_summary="",
        user_input="",
        response_message=None,
        decision=None,
        target_agent=None,
        order=[],
        final_price=None,
        memory_node=False
    )

    while True:
        print("Current State:\n" , state)
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye! 👋")
            break

        try:
            state["user_input"] = user_input
            state = graph.invoke(state, config=config)
            content = state["response_message"]
            print(f"\nAssistant: {content}")
            logger.info(f"Input: {user_input}")
        except Exception as e:
            logger.error(f"Graph error: {e}")
            print("Something went wrong. Can I help you with something else?")


if __name__ == "__main__":
    main()