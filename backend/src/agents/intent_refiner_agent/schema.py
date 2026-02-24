from pydantic import BaseModel, Field


class IntentRefinement(BaseModel):
    """Schema for intent refiner output."""
    
    refined_input: str = Field(
        ...,
        description="The rewritten user input with all references resolved"
    )