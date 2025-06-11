# coffee_shop_rag_pipeline.py

import os
import json
import re
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import JsonOutputParser
from langchain_pinecone import PineconeVectorStore
from pydantic import BaseModel, Field, validator
from typing import Optional

# ---- Pydantic model for filters ----

class QueryFilters(BaseModel):
    category: Optional[str] = None
    max_price: Optional[float] = Field(None, ge=0, le=100)
    min_rating: Optional[float] = Field(None, ge=0, le=5)

    @validator('category')
    def clean_category(cls, v):
        if v is None:
            return None
        v = v.strip().lower()
        if v in ["null", "none", ""]:
            return None
        return v.capitalize()

    @validator('max_price', 'min_rating', pre=True)
    def parse_float(cls, v):
        if v is None:
            return None
        if isinstance(v, (int, float)):
            return float(v)
        match = re.search(r"[\d.]+", str(v))
        if match:
            return float(match.group())
        return None

# ---- Main Pipeline Class ----

class CoffeeShopRAGPipeline:
    def __init__(self, vectorstore, groq_api_key, reranker=None):
        self.vectorstore = vectorstore
        self.reranker = reranker

        # Setup LLM for filter extraction
        self.llm_filter_extractor = ChatGroq(
            groq_api_key=groq_api_key,
            model_name="llama3-70b-8192",
            temperature=0.0
        )

        self.filter_prompt_template = PromptTemplate.from_template("""
You are a helpful assistant that extracts *structured filter parameters* from a user's natural language query about coffee shop products.

Extract the following fields:

- **category** (string or null) → e.g. "Coffee", "Tea", "Snack", etc.
- **max_price** (float or null)
- **min_rating** (float or null)

Hints:

- "cheap", "affordable", "budget" → max_price = 3.0
- "expensive", "premium" → min_rating = 4.5, max_price = null
- "highly rated", "top", "best" → min_rating = 4.5
- "under X dollars", "below X", "less than X" → max_price = X

If not mentioned, return null for the field.

Only return valid JSON like:

{{
  "category": "Coffee",
  "max_price": 3.0,
  "min_rating": 4.5
}}

User query: "{query}"

Extract and return JSON only.
""")

    def extract_filters(self, query):
        response = self.llm_filter_extractor.invoke(self.filter_prompt_template.format(query=query))
        
        try:
            filter_data = json.loads(response.content)
        except Exception as e:
            print(f"Filter extraction parse error: {e}, raw response:\n{response.content}")
            filter_data = {}
        
        return filter_data

    def postprocess_extracted_filters(self, filter_data):
        try:
            filters_obj = QueryFilters.parse_obj(filter_data)
            clean_filter = filters_obj.dict()
            print("Post-processed filters (via Pydantic):", clean_filter)
            return clean_filter
        except Exception as e:
            print(f"Pydantic parsing error: {e}, raw data: {filter_data}")
            return {
                "category": None,
                "max_price": None,
                "min_rating": None
            }

    def build_pinecone_filter(self, filters):
        pinecone_filter = {}
        if filters["category"]:
            pinecone_filter["category"] = {"$eq": filters["category"]}
        if filters["max_price"] is not None:
            pinecone_filter["price"] = {"$lte": filters["max_price"]}
        if filters["min_rating"] is not None:
            pinecone_filter["rating"] = {"$gte": filters["min_rating"]}
        
        print("Built Pinecone filter:", pinecone_filter)
        return pinecone_filter

    def retrieve(self, query, pinecone_filter=None):
        retriever = self.vectorstore.as_retriever(search_type="similarity", search_kwargs={
            "filter": pinecone_filter,
            "k": 10
        })
        docs = retriever.invoke(query)
        print(f"Retrieved {len(docs)} docs.")
        return docs

    def rerank_documents_llm(self, query, docs):
        doc_texts = [
            f"Document {i+1}:\n{doc.page_content}\nMetadata: {doc.metadata}"
            for i, doc in enumerate(docs)
        ]
        context = "\n\n".join(doc_texts)

        rerank_prompt = f"""
You are an expert reranker for a coffee shop product search engine.

User query: "{query}"

Here are the retrieved documents:

{context}

Instructions:
- Rank the documents in order of relevance to the user query.
- Consider metadata: category, price, rating.
- If user specified preferences, respect them.
- Respond with a list of document numbers like:

[2, 1, 3]

Only return the list of numbers.
"""
        response = self.llm_filter_extractor.invoke(rerank_prompt)

        try:
            doc_order = json.loads(response.content)
            reranked_docs = [docs[i-1] for i in doc_order]
            return reranked_docs
        except Exception as e:
            print(f"Reranker parse error: {e}, raw response:\n{response.content}")
            print("Falling back to original order.")
            return docs

    def run_pipeline(self, query):
        filters_raw = self.extract_filters(query)
        filters = self.postprocess_extracted_filters(filters_raw)
        pinecone_filter = self.build_pinecone_filter(filters)
        docs = self.retrieve(query, pinecone_filter)

        if self.reranker:
            reranked_docs = self.reranker(query, docs)
        else:
            reranked_docs = self.rerank_documents_llm(query, docs)

        return reranked_docs