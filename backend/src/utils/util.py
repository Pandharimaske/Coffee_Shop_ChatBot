import os
from dotenv import load_dotenv

load_dotenv()


# default_models.py

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

_llm_cache = {}

def load_llm(temperature: float = 0.0):
    if temperature not in _llm_cache:
        _llm_cache[temperature] = ChatGroq(model="llama-3.3-70b-versatile" , api_key=os.getenv("GROQ_API_KEY"))
    return _llm_cache[temperature]


async def call_llm_stream(prompt, temperature: float = 0.0):
    llm = load_llm(temperature)   # ✅ fetch from cache
    async for chunk in llm.astream(prompt):
        if chunk.content:
            yield chunk.content


# ---- Model Factories ----
def openai_gpt4o(**kwargs):
    """OpenAI GPT-4o-mini"""
    return ChatOpenAI(model="gpt-4o-mini", **kwargs)

def google_gemini(**kwargs):
    """Google Gemini 2.5 Pro"""
    return ChatGoogleGenerativeAI(model="gemini-2.5-pro",api_key = os.getenv("GEMINI_API_KEY"), **kwargs)

def openrouter_qwen(**kwargs):
    """OpenRouter Qwen (72B instruct as example)"""
    return ChatOpenAI(model="openai/gpt-oss-20b:free",base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY") , **kwargs)


# ---- Default stack (priority order) ----
DEFAULT_MODELS = [
    openai_gpt4o,
    google_gemini,
    openrouter_qwen,
]

from src.memory.supabase_client import supabase

def save_last_model(model_name: str):
    supabase.table("model_state").upsert({"id": "last_model", "value": model_name}).execute()

def load_last_model() -> str | None:
    res = supabase.table("model_state").select("value").eq("id", "last_model").execute()
    return res.data[0]["value"] if res.data else None



def reorder_models(models, last_model_name):
    if not last_model_name:
        return models
    for i, f in enumerate(models):
        if f.__name__ == last_model_name:
            # Move to front
            return [models[i]] + models[:i] + models[i+1:]
    return models

# fallback_llm.py
from typing import Callable, Optional, Type, List
from pydantic import BaseModel

def call_llm(
    prompt: str,
    schema: Optional[Type[BaseModel]] = None,
    temperature: float = 0.0,
    models: Optional[List[Callable]] = None,
):
    """
    Call LLM with fallback across multiple providers.
    Remembers last successful model and tries it first.
    """
    last_error = None
    model_factories = models or DEFAULT_MODELS
    
    # Reorder so last successful model is tried first
    last_model_name = load_last_model()
    model_factories = reorder_models(model_factories, last_model_name)
    
    for factory in model_factories:
        try:
            llm = factory(temperature=temperature)
            
            if schema:
                structured_llm = llm.with_structured_output(schema)
                result = structured_llm.invoke(prompt)
            else:
                result = llm.invoke(prompt)
            
            # Save success
            save_last_model(factory.__name__)
            return result
        
        except Exception as e:
            print(f"⚠️ {factory.__name__} failed: {e}")
            last_error = e
            continue
    
    raise RuntimeError(f"All models failed. Last error: {last_error}")



from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_pinecone import PineconeVectorStore
import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

embedding_model =  HuggingFaceEndpointEmbeddings(
    model=os.getenv("EMBEDDING_MODEL") , 
    huggingfacehub_api_token=os.getenv("HF_API_KEY")
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
