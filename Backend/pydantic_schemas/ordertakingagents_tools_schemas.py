from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class OrderItem(BaseModel):
    """Schema for a single ordered item."""
    name: str = Field(..., description="Name of the item ordered")
    quantity: int = Field(..., description="Quantity of the item ordered")


class OrderDetails(BaseModel):
    """Schema representing a full order with items and total cost."""
    products: List[OrderItem] = Field(..., description="List of ordered items")
    total: float = Field(..., description="Total cost of the order")


class ProductItem(BaseModel):
    """Schema for product + quantity input (used in ordering)."""
    name: str = Field(..., description="Name of the product")
    quantity: int = Field(..., description="Quantity of the product")
    per_unit_price: float = Field(..., description="Price of a single unit of the product")


class ProductOrderInput(BaseModel):
    """Input schema for placing an order with multiple products."""
    items: List[ProductItem] = Field(..., description="List of products with quantities")

class CheckAvailabilityInput(BaseModel):
    """Input schema for checking availability of multiple products."""
    product_names: List[str] = Field(..., description="List of product names to check availability for")


class ProductAvailability(BaseModel):
    """Output schema for availability status of a single product."""
    name: str = Field(..., description="Name of the product")
    available: bool = Field(..., description="Availability status")
    reason: Optional[str] = Field(None, description="Reason if not available")


class CheckAvailabilityOutput(BaseModel):
    """Output schema for availability results of multiple products."""
    results: List[ProductAvailability] = Field(..., description="Availability status for each product")


class GetPriceInput(BaseModel):
    """Input schema for getting prices of multiple products."""
    product_names: List[str] = Field(..., description="List of product names to get prices for")


class ProductPrice(BaseModel):
    """Schema for product name and its price."""
    name: str = Field(..., description="Name of the product")
    price: float = Field(..., description="Per-unit price of the product")


class GetPriceOutput(BaseModel):
    """Output schema for prices of multiple products."""
    prices: List[ProductPrice] = Field(..., description="List of product prices")


class FinalPriceOutput(BaseModel):
    """Output schema representing the final total after price calculation."""
    total: float = Field(..., description="Total cost including taxes or charges")