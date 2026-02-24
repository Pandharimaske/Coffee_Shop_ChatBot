from pydantic import BaseModel, Field
from typing import Optional, List


class DetailsResponse(BaseModel):
    """Schema for details agent response."""
    
    response_message: str = Field(
        ...,
        description="Friendly response to user query with product/shop information"
    )
    
    products_mentioned: Optional[List[str]] = Field(
        default=None,
        description="List of products mentioned in the response"
    )
    
    tools_used: Optional[List[str]] = Field(
        default=None,
        description="Tools used to generate this response"
    )
