import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

_llm_cache = {}

def load_llm(temperature: float = 0.0):
    if temperature not in _llm_cache:
        _llm_cache[temperature] = ChatGroq(model=os.getenv("GROQ_MODEL_NAME"), temperature=temperature)
    return _llm_cache[temperature]

