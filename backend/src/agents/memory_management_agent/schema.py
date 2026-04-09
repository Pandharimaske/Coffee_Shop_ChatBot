from pydantic import BaseModel, Field
from typing import Dict, Any


class MemoryIntent(BaseModel):
    reasoning: str = Field(description="Internal reasoning for why these updates are being made (or not made)")
    add_or_update: Dict[str, Any] = Field(default_factory=dict)
    remove: Dict[str, Any] = Field(default_factory=dict)
    replace: Dict[str, Any] = Field(default_factory=dict)

    def has_updates(self) -> bool:
        # Reasoning shouldn't trigger HITL on its own
        return bool(self.add_or_update or self.remove or self.replace)
