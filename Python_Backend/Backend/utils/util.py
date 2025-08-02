import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
# from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


def load_llm(temperature:float = 0):
    # return ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=temperature, api_key=os.getenv("GEMINI_API_KEY"))
    return ChatGroq(model=os.getenv("GROQ_MODEL_NAME"), temperature=temperature)