from typing import TypedDict, Literal , List
from pydantic import BaseModel , Field

class GuardAgentState(TypedDict):
    decision: Literal["allowed", "not allowed"]
    response_message: str
    chain_of_thought: str


class ClassificationAgentState(TypedDict):
    target_agent: str
    response_message: str
    chain_of_thought: str

class DetailsAgentState(TypedDict):
    response_message: str

class ProductItem(BaseModel):
    name: str = Field(..., description="Name of the product")
    quantity: int = Field(..., description="Quantity of the product")

class OrderInput(BaseModel):
    items: List[ProductItem]

class OrderTakingAgentState(TypedDict):
    order: OrderInput
    response_message: str