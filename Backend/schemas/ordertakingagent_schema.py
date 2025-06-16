from pydantic import BaseModel, Field
from typing import List, TypedDict


# ---- Schemas ----
class ProductItem(BaseModel):
    name: str = Field(..., description="Name of the product")
    quantity: int = Field(..., description="Quantity of the product")

class OrderInput(BaseModel):
    items: List[ProductItem]

class OrderTakingAgentState(TypedDict):
    order: OrderInput
    response_message: str