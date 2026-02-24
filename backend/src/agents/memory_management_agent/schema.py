from pydantic import BaseModel, Field
from typing import Dict, Any


class MemoryIntent(BaseModel):
    add_or_update: Dict[str, Any] = Field(default_factory=dict)
    remove: Dict[str, Any] = Field(default_factory=dict)
    replace: Dict[str, Any] = Field(default_factory=dict)

    def has_updates(self) -> bool:
        return bool(self.add_or_update or self.remove or self.replace)
