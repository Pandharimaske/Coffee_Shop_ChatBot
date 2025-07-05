from typing import TypedDict, Literal, Optional, List
from Backend.memory.user_memory import UserMemory

class ProductItem(TypedDict):
    name: str
    quantity: int
    per_unit_price: Optional[float]
    total_price: Optional[float]

class CoffeeAgentState(TypedDict):
    user_memory: UserMemory
    user_input: str
    response_message: Optional[str]
    decision: Optional[Literal["allowed", "not_allowed"]]
    target_agent: Optional[Literal["details_agent", "order_taking_agent", "recommendation_agent" , "update_order_agent"]]
    order: List[ProductItem]
    final_price: Optional[float]
    memory_node: bool