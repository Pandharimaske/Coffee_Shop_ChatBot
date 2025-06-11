from pydantic import BaseModel, Field
from typing import List


class ProductListInput(BaseModel):
    """Input schema for checking availability of products."""
    product_names: List[str] = Field(
        ..., 
        description="A list of product names to check for availability",
        example=["Cappuccino", "Latte"]
    )

class ProductQueryInput(BaseModel):
    """Input schema for product-related queries used in the RAG pipeline."""
    query: str = Field(
        ...,
        description="The user's query about coffee shop products, such as ingredients, categories, or descriptions."
    )

