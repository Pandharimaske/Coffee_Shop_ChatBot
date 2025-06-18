from typing import TypedDict, Literal , List , Optional
from pydantic import BaseModel , Field
from Backend.graph.states import ProductItem

class GuardAgentState(TypedDict):
    decision: Literal["allowed", "not allowed"]
    response_message: str


class ClassificationAgentState(TypedDict):
    target_agent: str
    response_message: str

class DetailsAgentState(TypedDict):
    response_message: str

class ProductItemInput(BaseModel):
    name: str = Field(..., description="Name of the product")
    quantity: int = Field(..., description="Quantity of the product")

class OrderInput(BaseModel):
    items: List[ProductItemInput]

class OrderTakingAgentState(TypedDict):
    order: List[ProductItem]
    response_message: str

class OrderUpdateItem(BaseModel):
    name: str = Field(..., description="Name of the product to update")

    # Option 1: absolute overwrite
    set_quantity: Optional[int] = Field(
        None,
        description="Set quantity to this value (overwrites current value)"
    )

    # Option 2: relative update
    delta_quantity: Optional[int] = Field(
        None,
        description="Change quantity by this amount (positive = add, negative = remove)"
    )


class OrderUpdateState(BaseModel):
    updates: List[OrderUpdateItem] = Field(..., description="List of order updates")