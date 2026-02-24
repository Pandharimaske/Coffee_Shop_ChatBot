"""Schemas for Coffee Shop tools — input and output models."""

from pydantic import BaseModel, Field
from typing import List, Optional


# ── Input Schemas ─────────────────────────────────────────────────────────────

class ProductQueryInput(BaseModel):
    """Input for semantic product search."""
    query: str = Field(..., description="Natural language query e.g. 'sweet pastry', 'cold brew'")
    top_k: Optional[int] = Field(default=5, description="Number of results to return (default: 5)")


class ProductInfoInput(BaseModel):
    """Input for fetching specific product details by name."""
    product_names: List[str] = Field(..., description="List of product names e.g. ['Cappuccino', 'Latte']")


class AboutUsInput(BaseModel):
    """Input for shop information tool (optional filter)."""
    query: Optional[str] = Field(default="", description="Optional filter — usually left empty")


# ── Output Schemas ────────────────────────────────────────────────────────────

class ProductItem(BaseModel):
    """A single product with full details."""
    name: str = Field(..., description="Product name")
    price: float = Field(..., description="Price in rupees")
    rating: Optional[float] = Field(None, description="Rating out of 5")
    category: Optional[str] = Field(None, description="e.g. Coffee, Bakery")
    description: Optional[str] = Field(None, description="Product description")
    is_available: Optional[bool] = Field(True, description="Whether the item is in stock")
    score: Optional[float] = Field(None, description="Search relevance score")


class ProductInfoOutput(BaseModel):
    """Output from the product info tool."""
    products: List[ProductItem] = Field(..., description="List of matched products")
    count: Optional[int] = Field(None, description="Number of products returned")


class AboutUsOutput(BaseModel):
    """Output from the shop info tool."""
    content: str = Field(..., description="Shop info: hours, location, story, specialties")
    source: str = Field(default="AboutUsTool")
