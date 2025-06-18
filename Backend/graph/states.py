from typing import TypedDict, Literal, Optional, List

class ProductItem(TypedDict):
    name: str
    quantity: int
    per_unit_price: Optional[float]
    total_price: Optional[float]

class InputState(TypedDict):
    user_input: str

class OutputState(TypedDict):
    response_message: str

class CoffeeAgentState(TypedDict):
    user_name:str = "Pandhari"
    user_input: str
    response_message: Optional[str]
    decision: Optional[Literal["allowed", "not_allowed"]]
    target_agent: Optional[Literal["details_agent", "order_taking_agent", "recommendation_agent" , "update_order_agent"]]
    order: List[ProductItem]
    final_price: Optional[float]