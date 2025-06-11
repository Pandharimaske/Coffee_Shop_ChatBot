from langchain.tools import Tool
from Backend.pydantic_schemas.agents_schemas import ProductOrderInput , ProductItem
from Backend.retriever import retriever

def calculate_final_price_func(order: ProductOrderInput) -> str:
    total_price = 0.0
    breakdown = []

    for item in order.items:
        query = item.name.strip().lower()
        results = retriever.invoke(query)
        found = False
        for doc in results:
            if query in doc.metadata["name"].lower():
                price = float(doc.metadata.get("price", 0.0))
                item_total = price * item.quantity
                total_price += item_total
                breakdown.append(f"{doc.metadata['name']} x {item.quantity} = ${item_total:.2f}")
                found = True
                break
        if not found:
            breakdown.append(f"{item.name.title()} not found or unavailable.")

    breakdown.append(f"\n🧾 Final Total: ${total_price:.2f}")
    return "\n".join(breakdown)

calculate_final_price_tool = Tool.from_function(
    name="calculate_final_price",
    func=calculate_final_price_func,
    description="Calculate the total price of a list of products with their quantities.",
    args_schema=ProductOrderInput,
)