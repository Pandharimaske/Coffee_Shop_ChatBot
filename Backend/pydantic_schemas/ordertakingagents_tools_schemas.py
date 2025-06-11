from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class OrderItem(BaseModel):
    """Schema for a single ordered item."""
    item: str = Field(..., description="Name of the item ordered")
    quantity: int = Field(..., description="Quantity of the item ordered")


class OrderDetails(BaseModel):
    """Schema representing a full order with items and total cost."""
    items: List[OrderItem] = Field(..., description="List of ordered items")
    total: float = Field(..., description="Total cost of the order")


class ProductItem(BaseModel):
    """Schema for product + quantity input (used in ordering)."""
    name: str = Field(..., description="Name of the product")
    quantity: int = Field(..., description="Quantity of the product")


class ProductOrderInput(BaseModel):
    """Input schema for placing an order with multiple products."""
    items: List[ProductItem] = Field(..., description="List of products with quantities")
