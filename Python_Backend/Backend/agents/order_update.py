from Backend.schemas.state_schema import OrderUpdateState
from Backend.graph.states import CoffeeAgentState
from Backend.utils.logger import logger
from Backend.utils.util import load_llm , load_vectorstore



# ---- Order Update Agent Class ----
class OrderUpdateAgent:
    def __init__(self):
        self.llm = load_llm().with_structured_output(OrderUpdateState)
        self.vectorstore = load_vectorstore()
        logger.info("OrderUpdateAgent initialized")


    def update_order(self , state: CoffeeAgentState) -> CoffeeAgentState:
        update_input = self.llm.invoke(state["user_input"])
        print(update_input)

        logger.debug(f"🔍 Parsed updates: {update_input.updates}")

        order_dict = {item["name"].lower(): item for item in state["order"]}

        for update in update_input.updates:
            item_name = update.name.strip().lower()
            current_item = order_dict.get(item_name)

            results = self.vectorstore.similarity_search(
                query="",
                k=1,
                filter={"name": {"$eq": update.name.strip().title()}}
            )
            price = results[0].metadata.get("price", 0.0) if results else 0.0


            if update.set_quantity is not None:
                if update.set_quantity > 0:
                    total_price = price * update.set_quantity
                    order_dict[item_name] = {
                        "name": update.name,
                        "quantity": update.set_quantity,
                        "per_unit_price": price,
                        "total_price": total_price
                    }
                else:
                    order_dict.pop(item_name, None)

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
                else:
                    if update.delta_quantity > 0:
                        total_price = price * update.delta_quantity
                        order_dict[item_name] = {
                            "name": update.name,
                            "quantity": update.delta_quantity,
                            "per_unit_price": price,
                            "total_price": total_price
                        }

        state["order"] = list(order_dict.values())

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

        return state