import asyncio
import uuid
from pprint import pprint
from src.graph.graph import build_coffee_shop_graph
from src.graph.state import CoffeeAgentState
from src.memory.memory_manager import get_user_memory
from src.orders import get_active_order


async def run_chatbot():
    app = build_coffee_shop_graph()

    # ── Dev: hardcoded user. Replace with login session after auth is built ──
    user_id = "dev@merrysway.coffee"

    config = {
        "configurable": {
            "thread_id": str(uuid.uuid4()),
            "user_id": user_id,
        }
    }

    # Load persisted memory + active order from Supabase at session start
    try:
        user_memory = get_user_memory(user_id)
    except Exception:
        user_memory = None

    try:
        order, final_price = get_active_order(user_id)
    except Exception:
        order, final_price = [], 0.0

    state = CoffeeAgentState(
        user_memory=user_memory or CoffeeAgentState().user_memory,
        order=order,
        final_price=final_price,
    )

    print("--- Coffee Shop Chatbot Test Mode ---")
    print(f"User: {user_id}")
    print("Type '/exit' to quit.\n")

    while True:
        user_input = input("User: ")
        if user_input.lower() == "/exit":
            break

        if isinstance(state, dict):
            state['user_input'] = user_input
        else:
            state.user_input = user_input

        print("\n" + "=" * 50)
        print("PRE-GRAPH STATE:")
        pprint(state.model_dump() if hasattr(state, 'model_dump') else state)
        print("=" * 50)

        final_state = await app.ainvoke(state, config=config)
        state = final_state

        print("\n" + "=" * 50)
        print("POST-GRAPH STATE:")
        pprint(final_state)
        print("=" * 50)

        if final_state.get('response_message'):
            print(f"\n[Bot]: {final_state.get('response_message')}")

        print("\n")


if __name__ == "__main__":
    try:
        asyncio.run(run_chatbot())
    except KeyboardInterrupt:
        print("\nExiting...")
