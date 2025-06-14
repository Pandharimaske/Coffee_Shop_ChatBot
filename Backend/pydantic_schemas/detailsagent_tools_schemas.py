from pydantic import BaseModel, Field
from typing import List, Dict


class AvailabilityInput(BaseModel):
    """Schema to check which products are available in the coffee shop."""
    product_names: List[str] = Field(
        ..., 
        description="List of products with their names to check for availability.",
        example=[
            {"name": "Cappuccino"}
        ]
    )

class ProductQueryInput(BaseModel):
    """Schema for natural language queries about products (for use in RAG pipelines)."""
    query: str = Field(
        ...,
        description="User query related to product details, such as ingredients, description, or category.",
        example="What are the ingredients in the Mocha?"
    )

class PriceCheckItem(BaseModel):
    name: str = Field(..., description="Name of the product.")
    is_available: bool = Field(..., description="Availability status of the product.")

class PriceCheckInput(BaseModel):
    """Schema for checking prices of available or unavailable products."""
    product_names: List[PriceCheckItem] = Field(
        ...,
        description="List of products with name, availability status.",
        example=[
            {"name": "Latte", "is_available": True},
            {"name": "Samosa", "is_available": False}
        ]
    )
    
class ProductPriceInfo(BaseModel):
    """Information about an individual product's name, availability, price."""
    name: str = Field(..., description="The name of the product (e.g., Latte).")
    is_available: bool = Field(..., description="Indicates whether the product is available.")
    price: float = Field(..., description="Price of the product. Zero if unavailable or not found.")

class ProductPriceListOutput(BaseModel):
    """List of products with their availability and price information."""
    products: List[ProductPriceInfo] = Field(
        ..., description="List of product price and availability entries."
    )