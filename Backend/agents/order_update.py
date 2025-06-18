from Backend.graph.states import ProductItem
from Backend.schemas.state_schema import OrderUpdateState
from Backend.graph.states import CoffeeAgentState
from Backend.utils.logger import logger
from Backend.utils.util import load_llm
from langchain.output_parsers import PydanticOutputParser
from Backend.prompts.order_updates_prompt import update_order_prompt
from langchain_core.runnables import RunnableSequence
from Backend.Tools.detailsagents_tools.retriever_tool import vectorstore



# ---- Order Update Agent Class ----
class OrderUpdateAgent:
    def __init__(self):
        self.llm = load_llm()
        self.parser = PydanticOutputParser(pydantic_object=OrderUpdateState)
        self.parse_prompt = update_order_prompt

        self.llm_parser_chain: RunnableSequence = (
            self.parse_prompt.partial(format_instructions=self.parser.get_format_instructions())
            | self.llm
            | self.parser
        )

        logger.info("OrderUpdateAgent initialized")

    def parse_user_input(self, user_input: str) -> OrderUpdateState:
        return self.llm_parser_chain.invoke({"user_input": user_input})

    def get_response(self, user_input: str) -> OrderUpdateState:
        try:
            logger.info(f"User input (update): {user_input}")
            parsed_update = self.parse_user_input(user_input)
            logger.info(f"Parsed order update: {parsed_update}")
            return parsed_update
        except Exception as e:
            logger.error(f"OrderUpdateAgent error: {e}")
            return OrderUpdateState(updates=[])

def update_order(state: CoffeeAgentState) -> CoffeeAgentState:
    print("🛠️ [update_order] Entered update_order function.")
    logger.info("🛠️ Entered update_order function.")

    # Ensure 'order' key exists
    if "order" not in state:
        logger.warning("⚠️ 'order' key missing in state. Initializing empty order list.")
        state["order"] = []

    # Extract updates using LLM
    agent = OrderUpdateAgent()
    update_input = agent.get_response(state["user_input"])

    logger.debug(f"🔍 Parsed updates: {update_input.updates}")

    # Convert existing order to a dictionary for easier updates
    order_dict = {item["name"].lower(): item for item in state["order"]}
    logger.debug(f"🧾 Existing order dict: {order_dict}")

    for update in update_input.updates:
        item_name = update.name.strip().lower()
        current_item = order_dict.get(item_name)

        # Get price from vectorstore
        results = vectorstore.similarity_search(
            query="",
            k=1,
            filter={"name": {"$eq": update.name.strip().title()}}
        )
        price = results[0].metadata.get("price", 0.0) if results else 0.0

        logger.debug(f"💵 Price lookup for {update.name.strip().title()}: ₹{price}")

        if update.set_quantity is not None:
            if update.set_quantity > 0:
                total_price = price * update.set_quantity
                order_dict[item_name] = {
                    "name": update.name,
                    "quantity": update.set_quantity,
                    "per_unit_price": price,
                    "total_price": total_price
                }
                logger.info(f"✅ Set quantity for {update.name}: {update.set_quantity}")
            else:
                order_dict.pop(item_name, None)
                logger.info(f"❌ Removed item due to zero quantity: {update.name}")

        elif update.delta_quantity is not None:
            if current_item:
                new_quantity = current_item["quantity"] + update.delta_quantity
                if new_quantity > 0:
                    total_price = price * new_quantity
                    order_dict[item_name]["quantity"] = new_quantity
                    order_dict[item_name]["per_unit_price"] = price
                    order_dict[item_name]["total_price"] = total_price
                    logger.info(f"🔁 Updated {update.name} to quantity: {new_quantity}")
                else:
                    order_dict.pop(item_name, None)
                    logger.info(f"❌ Removed item after delta update: {update.name}")
            else:
                if update.delta_quantity > 0:
                    total_price = price * update.delta_quantity
                    order_dict[item_name] = {
                        "name": update.name,
                        "quantity": update.delta_quantity,
                        "per_unit_price": price,
                        "total_price": total_price
                    }
                    logger.info(f"➕ Added new item {update.name} with quantity: {update.delta_quantity}")

    state["order"] = list(order_dict.values())
    logger.debug(f"🛒 Final order: {state['order']}")

    # Create a summary response
    if state["order"]:
        summary = "\n".join(
            f"🛍️ {item['name']} x {item['quantity']} @ ₹{item['per_unit_price']} = ₹{item['total_price']}"
            for item in state["order"]
        )
        final_total = sum(item["total_price"] or 0 for item in state["order"])
        state["response_message"] = f"✅ Your order has been updated:\n{summary}\n\n🧾 Total: ₹{final_total:.2f}"
        state["final_price"] = final_total
        logger.info(f"✅ Order updated successfully. Total: ₹{final_total:.2f}")
    else:
        state["response_message"] = "Your order is now empty."
        state["final_price"] = 0.0
        logger.info("🧹 Order is now empty.")

    print("✅ [update_order] Finished update_order function.")
    return state