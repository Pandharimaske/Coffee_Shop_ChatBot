from langchain.tools import Tool
from src.schemas.detailsagent_tools_schemas import AvailabilityInput, PriceCheckInput
from src.utils.util import load_vectorstore

def check_availability_func(product_names: AvailabilityInput) -> PriceCheckInput:
    """
    Check the availability of a list of product names using metadata filtering.
    Returns a PriceCheckInput structure.
    """
    availability_list = []

    for name in product_names:
        name_lower = name.strip().title()

        results = load_vectorstore().similarity_search(
            query="",  
            k=1,
            filter={"name": {"$eq": name_lower}}
        )

        is_available = bool(results)

        availability_list.append({
            "name": name.title(),
            "is_available": is_available,
        })

    return PriceCheckInput(product_names=availability_list)

check_availability_tool = Tool.from_function(
    name="CheckAvailabilityTool",
    func=check_availability_func,
    description="Check if products are available in the shop. Input is a list of product names.",
    args_schema=AvailabilityInput
)