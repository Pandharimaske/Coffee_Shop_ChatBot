from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class OrderAction(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    CANCEL = "cancel"
    CONFIRM = "confirm"


class ProductItemInput(BaseModel):
    """A single item in a new order request."""
    name: str = Field(..., description="Name of the product")
    quantity: int = Field(..., description="Quantity of the product")


class OrderInput(BaseModel):
    """Parsed new order from user input."""
    items: List[ProductItemInput] = Field(..., description="List of items to order")


class OrderUpdateItem(BaseModel):
    """A single item modification."""
    name: str = Field(..., description="Product name")
    set_quantity: Optional[int] = Field(default=None, description="Set exact quantity (0 = remove)")
    delta_quantity: Optional[int] = Field(default=None, description="Add/subtract from current quantity")


class OrderUpdateState(BaseModel):
    """Parsed order update from user input."""
    updates: List[OrderUpdateItem] = Field(..., description="List of order modifications")


class OrderItem(BaseModel):
    """Single item in a confirmed order."""
    name: str = Field(..., description="Product name")
    quantity: int = Field(..., description="Quantity ordered")
    per_unit_price: float = Field(default=0.0, description="Price per unit")
    total_price: float = Field(default=0.0, description="Total price for this item")


class OrderSummary(BaseModel):
    """Summary of a processed order."""
    items: List[OrderItem] = Field(..., description="Items in the order")
    available_items: List[str] = Field(default_factory=list)
    unavailable_items: List[str] = Field(default_factory=list)
    total: float = Field(default=0.0)
    message: str = Field(..., description="Summary message for the user")


class ActionDecision(BaseModel):
    """LLM decision on what action the user wants."""
    action: OrderAction = Field(..., description="The detected order action")
