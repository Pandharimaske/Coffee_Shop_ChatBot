import os
from dotenv import load_dotenv
# from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

load_dotenv()

_llm_cache = {}

def load_llm(temperature: float = 0.0):
    if temperature not in _llm_cache:
        _llm_cache[temperature] = ChatOpenAI(model="gpt-4o-mini" , api_key=os.getenv("OPENAI_API_KEY"))
    return _llm_cache[temperature]

# from langchain_openai import ChatOpenAI

# _llm_cache = {}

# def load_llm(temperature: float = 0.0):
#     if temperature not in _llm_cache:
#         _llm_cache[temperature] = ChatOpenAI(
#             model="qwen/qwen3-coder:free",
#             temperature=temperature,
#             base_url="https://openrouter.ai/api/v1",
#             api_key=os.getenv("OPENROUTER_API_KEY")
#         )
#     return _llm_cache[temperature]


from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
from pinecone import Pinecone, ServerlessSpec

embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=os.getenv("GEMINI_API_KEY")
)
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = "coffee-products"
if index_name not in pc.list_indexes().names():
    pc.create_index(
        index_name,
        dimension=768,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
index = pc.Index(index_name)

vectorstore = PineconeVectorStore(
    index=index,
    embedding=embedding_model,
    text_key="text"
)

def load_vectorstore():
    return vectorstore
