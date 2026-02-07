from typing import Dict, Union
from src.utils.util import call_llm
from src.prompts.memory_prompts import memory_update_prompt
from pydantic import BaseModel, ValidationError


class MemoryUpdateAgent:
    class MemoryIntent(BaseModel):
        add_or_update: Dict[str, Union[str, list]] = {}
        remove: Dict[str, Union[str, list]] = {}

    def __init__(self):
        pass

    def extract_memory_action(self, user_input: str) -> Dict:
        try:
            prompt = memory_update_prompt.invoke({"user_input": user_input})
            return call_llm(prompt=prompt , schema=self.MemoryIntent)
        except ValidationError as e:
            print(f"[MemoryUpdateAgent] Validation error: {e}")
            return {"add_or_update": {}, "remove": {}}