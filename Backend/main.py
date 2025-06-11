from Backend.graph.coffee_shop_graph import build_coffee_shop_graph  # Update to your complete graph file
from Backend.utils.logger import logger


def main():
    graph = build_coffee_shop_graph()
    logger.info("Coffee Shop Bot initialized")

    print("☕ Welcome to the Coffee Shop Bot! Ask anything or type 'exit' to quit.")

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye! 👋")
            break

        try:
            # Initial input to the graph
            result = graph.invoke({"input": user_input})

            # Final output message from routed agent
            content = result.get("content", "No content generated.")

            print(f"\nAssistant: {content}")
            logger.info(f"Input: {user_input}")
        except Exception as e:
            logger.error(f"Graph error: {e}")
            print("Something went wrong. Can I help you with something else?")

if __name__ == "__main__":
    main()
    """python -m Backend.main"""
