import json
import os
from dotenv import load_dotenv
load_dotenv()
from langchain_core.tools import Tool
from Backend.rag_pipeline import CoffeeShopRAGPipeline
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from pinecone import Pinecone, ServerlessSpec
from Backend.pydantic_schemas.detailsagent_tools_schemas import ProductQueryInput

# Setup embedding + vectorstore + pipeline once
embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-base-en-v1.5")
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = "coffee-products"
if index_name not in pc.list_indexes().names():
    pc.create_index(
        index_name,
        dimension=768,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
index = pc.Index(index_name)

vectorstore = PineconeVectorStore(
    index=index,
    embedding=embedding_model,
    text_key="text"
)

rag_pipeline = CoffeeShopRAGPipeline(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    vectorstore=vectorstore
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
    retrieve_coffee_docs.last_docs = docs  # optional, for DetailsAgent postprocessing

    result_lines = []
    for doc in docs:
        meta = doc.metadata
        result_lines.append(
            f"Name: {meta.get('name')}\n"
            f"Category: {meta.get('category')}\n"
            f"Price: ${meta.get('price')}\n"
            f"Rating: {meta.get('rating')}\n"
            "-----------------------------"
        )

    return "\n".join(result_lines)

# Define Tool
def rag_tool_func(input_data: ProductQueryInput) -> str:
    return retrieve_coffee_docs(input_data)

rag_tool = Tool.from_function(
    name="CoffeeShopProductRetriever",
    func=rag_tool_func,
    description="Use this tool to retrieve coffee shop product documents relevant to a user query if additional information is needed.",
    args_schema=ProductQueryInput
)