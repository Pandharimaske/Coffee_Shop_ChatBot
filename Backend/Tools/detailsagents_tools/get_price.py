from langchain.tools import Tool
from Backend.Tools.detailsagents_tools.retriever_tool import vectorstore
from Backend.pydantic_schemas.detailsagent_tools_schemas import ProductListInput

def get_price_func(product_names:ProductListInput) -> str:
    responses = []
    for name in product_names:
        query = name.strip().lower()
        retriever_instance = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 2})
        results = retriever_instance.invoke(query)
        found = False
        for doc in results:
            if query in doc.metadata["name"].lower():
                price = doc.metadata.get("price", "N/A")
                responses.append(f"💲 {doc.metadata['name']}: ${price}")
                found = True
                break
        if not found:
            responses.append(f"❌ {name.title()}: Price not found.")
    return "\n".join(responses)

get_price_tool = Tool.from_function(
    name="GetPriceTool",
    func=get_price_func,
    description=(
        "Provide a JSON object with a list of product names under key 'product_names'. "
        "Example valid input: {\"product_names\": [\"Latte\", \"Cappuccino\"]}. "
        "Do NOT provide a single string — always provide a list, even for one product."
    ),
    args_schema=ProductListInput
)