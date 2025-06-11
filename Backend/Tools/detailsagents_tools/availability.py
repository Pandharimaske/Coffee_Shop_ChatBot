import json
from langchain.tools import Tool
from Backend.pydantic_schemas.detailsagent_tools_schemas import ProductListInput
from Backend.Tools.detailsagents_tools.retriever_tool import vectorstore
from Backend.pydantic_schemas.agents_schemas import ProductListInput

def check_availability_func(product_names: ProductListInput) -> str:
    """
    Check the availability of a list of product names in the coffee shop's database.

    Args:
        input_data (ProductListInput): A Pydantic model containing a list of product names.

    Returns:
        str: A JSON-formatted string containing availability information for each product.
             Each entry will have:
                 - product: name of the product
                 - available: True or False
                 - reason (optional): reason if the product is not available
    """
    availability_list = []
    for name in product_names:
        query = name.strip().lower()
        retriever_instance = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 2})
        results = retriever_instance.invoke(query)
        found = False
        for doc in results:
            if query in doc.metadata["name"].lower():
                availability_list.append({"product": doc.metadata["name"], "available": True})
                found = True
                break
        if not found:
            availability_list.append({"product": name.title(), "available": False, "reason": "Product not found"})
    return json.dumps(availability_list, indent=2)

check_availability_tool = Tool.from_function(
    name="CheckAvailabilityTool",
    func=check_availability_func,
    description="Check if products are available in the shop. Input is a list of product names.",
    args_schema=ProductListInput  # ✅ Add this!
)