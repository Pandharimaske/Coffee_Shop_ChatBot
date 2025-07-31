from Backend.utils.logger import logger
from Backend.utils.util import load_llm
from Backend.Tools.retriever_tool import vectorstore
from Backend.schemas.state_schema import OrderInput
from Backend.graph.states import ProductItem
from typing import List

# ---- Agent Class ----
class OrderTakingAgent:
    def __init__(self):
        self.llm = load_llm().with_structured_output(OrderInput)
        logger.info("OrderAgent initialized")

    def place_order(self, order: OrderInput) -> tuple[str, list[ProductItem] , float]:
        items = order.items
        available_items: List[ProductItem] = []
        unavailable_items = []
        total = 0
        summary_lines = []

        for item in items:
            name = item.name.strip().title()
            results = vectorstore.similarity_search(
                query="",
                k=1,
                filter={"name": {"$eq": name}}
            )

            if results:
                doc = results[0]
                price = doc.metadata.get("price", 0.0)
                line_total = item.quantity * price
                available_items.append({
                    "name": item.name,
                    "quantity": item.quantity,
                    "per_unit_price": price,
                    "total_price": line_total
                })
                total += line_total
                summary_lines.append(f"✅ {name} x {item.quantity} @ ${price} = ${line_total}")
            else:
                unavailable_items.append(name)

        summary = "\n".join(summary_lines)

        if unavailable_items:
            unavailable = "\n".join(f"❌ {name}" for name in unavailable_items)
            summary += (
                f"\n\nTotal (for available items): ${total}\n\n"
                f"However, some items that we don't serve in our coffee shop:\n{unavailable}\n"
                f"Would you like to replace them?"
            )
        else:
            summary += f"\n\nTotal: ${total}\nShall I place the order?"

        return summary, available_items , total


    def get_response(self, user_input: str) -> dict:
        try:
            logger.info(f"User input: {user_input}")
            parsed_order = self.llm.invoke(user_input)
            print(parsed_order)
            logger.info(f"Parsed order: {parsed_order}")
            summary, filtered_order , total = self.place_order(parsed_order)

            return {
                "order": filtered_order,
                "response_message": summary , 
                "final_price": total
            }
        except Exception as e:
            logger.error(f"OrderAgent error: {e}")
            return {
                "order": [],
                "response_message": "Sorry, I couldn’t process your order. Could you please rephrase it?",
                "final_price": 0
            }