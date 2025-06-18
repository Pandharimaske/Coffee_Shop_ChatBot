from Backend.graph.coffee_shop_graph import build_coffee_shop_graph
from Backend.graph.states import CoffeeAgentState
from Backend.utils.logger import logger


def main():
    graph = build_coffee_shop_graph()
    logger.info("Coffee Shop Bot initialized")

    print("☕ Welcome to the Coffee Shop Bot! Ask anything or type 'exit' to quit.")

    # ✅ Start with full CoffeeAgentState
    state = CoffeeAgentState(
        user_name="Pandhari",
        user_input="",
        response_message=None,
        decision=None,
        target_agent=None,
        order = [],
        final_price = None
        )

    while True:
        print(f"\n📥 Current State (Before Input): {state}")
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye! 👋")
            break

        try:
            # ✅ Update state with latest user input
            state["user_input"] = user_input

            # ✅ Invoke graph and get updated state back
            state = graph.invoke(state)
            print(f"\n📤 Updated State (After Graph): {state}")

            # ✅ Extract and print the assistant’s response
            content = state["response_message"] or "Sorry, I can't help with that."
            print(f"\nAssistant: {content}")
            logger.info(f"Input: {user_input}")
        except Exception as e:
            logger.error(f"Graph error: {e}")
            print("Something went wrong. Can I help you with something else?")


if __name__ == "__main__":
    main()