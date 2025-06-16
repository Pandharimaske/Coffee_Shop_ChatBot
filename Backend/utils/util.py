import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()
llm = ChatGroq(name=os.getenv("GROQ_MODEL_NAME"), temperature=0)