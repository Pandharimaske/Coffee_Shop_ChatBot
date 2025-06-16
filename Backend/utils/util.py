import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

def load_llm():
    return ChatGroq(model=os.getenv("GROQ_MODEL_NAME"), temperature=0)