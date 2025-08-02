from langchain_core.tools import Tool
from Backend.rag_pipeline import CoffeeShopRAGPipeline
from Backend.schemas.detailsagent_tools_schemas import ProductQueryInput
from Backend.utils.util import load_vectorstore

rag_pipeline = CoffeeShopRAGPipeline(
    vectorstore=load_vectorstore()
)

# Tool function
def retrieve_coffee_docs(query: str) -> str:
    """
    Retrieve coffee shop product documents matching the user query.

    Args:
        query (str): The user query for the coffee product(s).

    Returns:
        str: A formatted plain text string with product details.
    """
    docs = rag_pipeline.run_pipeline(query)

    result_lines = []
    for doc in docs:
        result_lines.append(doc.page_content)
    return "\n\n".join(result_lines)

# Define Tool
def rag_tool_func(input_data: ProductQueryInput) -> str:
    return retrieve_coffee_docs(input_data)

rag_tool = Tool.from_function(
    name="CoffeeShopProductRetriever",
    func=rag_tool_func,
    description="Use this tool to retrieve coffee shop product documents relevant to a user query if additional information is needed.",
    args_schema=ProductQueryInput
)