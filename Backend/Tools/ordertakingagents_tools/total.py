from langchain.tools import Tool
from Backend.pydantic_schemas.detailsagent_tools_schemas import ProductPriceListOutput

def calculate_final_price_func(order: ProductPriceListOutput) -> str:
    total_price = 0.0
    breakdown = []

    for item in order.products:
        if item.is_available:
            item_total = item.price * item.quantity
            total_price += item_total
            breakdown.append(f"{item.name} x {item.quantity} = ${item_total:.2f}")
            
    breakdown.append(f"\n🧾 Final Total: ${total_price:.2f}")
    return "\n".join(breakdown)

calculate_final_price_tool = Tool.from_function(
    name="calculate_final_price",
    func=calculate_final_price_func,
    description="Calculate the total price of all available products with their quantities.",
    args_schema=ProductPriceListOutput,
    return_direct=True
)