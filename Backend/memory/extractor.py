from typing import Dict, Union
from Backend.utils.util import load_llm
from Backend.prompts.memory_prompts import memory_update_prompt
from pydantic import BaseModel, ValidationError
from langchain.output_parsers import PydanticOutputParser


class MemoryUpdateAgent:
    class MemoryIntent(BaseModel):
        add_or_update: Dict[str, Union[str, list]] = {}
        remove: Dict[str, Union[str, list]] = {}

    def __init__(self):
        self.llm = load_llm()
        self.parser = PydanticOutputParser(pydantic_object=self.MemoryIntent)
        self.prompt = memory_update_prompt
        self.chain = self.prompt | self.llm | self.parser

    def extract_memory_action(self, user_input: str) -> Dict:
        try:
            return self.chain.invoke({"user_input": user_input})
        except ValidationError as e:
            print(f"[MemoryUpdateAgent] Validation error: {e}")
            return {"add_or_update": {}, "remove": {}}