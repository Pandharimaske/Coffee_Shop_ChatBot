"""Scalable Retriever helpers for Coffee Shop RAG - Supabase pgvector version

Provides utilities to query Supabase with vector similarity search for:
- Hybrid lookup (Exact match + Semantic fallback)
- Unified product data & pricing source of truth
- Low latency search (<300ms)
- Multi-user / Multi-tenant support
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

import dotenv
from langchain_huggingface import HuggingFaceEndpointEmbeddings

from src.config import Config, RetrieverConfig as ConfigRetrieverConfig
from src.memory.supabase_client import supabase_admin as supabase

dotenv.load_dotenv()

logger = logging.getLogger(__name__)

# Use centralized RetrieverConfig from src/config.py
RetrieverConfig = ConfigRetrieverConfig


class PooledRetriever:
    """Manages pooled connections for embeddings."""

    _instance = None
    _embedding_cache = {}

    def __new__(cls):
        """Singleton pattern for connection pooling."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        Config.validate()
        self._initialized = True
        logger.info("PooledRetriever initialized with Supabase pgvector support")

    def get_embeddings(self, model: Optional[str] = None) -> HuggingFaceEndpointEmbeddings:
        """Get or create embeddings model (cached)."""
        model = model or Config.EMBEDDING_MODEL
        
        if model not in PooledRetriever._embedding_cache:
            try:
                PooledRetriever._embedding_cache[model] = HuggingFaceEndpointEmbeddings(
                    model=model,
                    huggingfacehub_api_token=Config.HF_API_KEY
                )
                logger.info(f"Embeddings model cached: {model}")
            except Exception as e:
                logger.error(f"Failed to initialize embeddings model {model}: {str(e)}")
                raise
        
        return PooledRetriever._embedding_cache[model]

    @classmethod
    def clear_cache(cls):
        """Clear all caches."""
        cls._embedding_cache.clear()
        logger.info("PooledRetriever cache cleared")


# Convenience singleton
_pooled_retriever = PooledRetriever()


def search_products(
    query: str,
    top_k: int = 5,
    match_threshold: float = 0.5,
) -> List[Dict[str, Any]]:
    """Search products using Supabase pgvector similarity search.

    Args:
        query: Natural language search query
        top_k: Number of results to return
        match_threshold: Minimum similarity score (0 to 1)

    Returns:
        List of product dicts with name, price, similarity, etc.
    """
    try:
        embeddings = _pooled_retriever.get_embeddings()
        q_vec = embeddings.embed_query(query)
        
        # Call the Supabase RPC function 'match_coffee_products'
        rpc_params = {
            'query_embedding': q_vec,
            'match_threshold': match_threshold,
            'match_count': top_k
        }
        
        res = supabase.rpc('match_coffee_products', rpc_params).execute()
        
        if not res.data:
            return []
            
        results = []
        for p in res.data:
            results.append({
                "id": p.get("id"),
                "name": p.get("name"),
                "price": p.get("price"),
                "score": p.get("similarity"), # Map similarity to score for backward compatibility
                "category": p.get("category"),
                "description": p.get("description"),
                "image_url": p.get("image_url"),
                "metadata": p
            })
            
        return results
    except Exception as e:
        logger.error(f"Supabase vector search failed: {str(e)}")
        return []


def get_product_by_name(name: str) -> Dict[str, Any]:
    """Fetch product by name with Hybrid Logic using Supabase ONLY:
    1. Try exact lookup in Supabase.
    2. Fallback to Supabase pgvector semantic search to "translate" misspelt names.
    """
    try:
        normalized = name.lower().strip()
        
        # --- Step 1: Direct Supabase Lookup (Exact/ILIKE) ---
        res = supabase.table("coffee_shop_products").select("*").ilike("name", normalized).execute()
        
        if res.data:
            p = res.data[0]
            logger.debug(f"Direct Supabase match found for '{name}'")
            return {
                "found": True,
                "name": p.get("name"),
                "price": p.get("price"),
                "image_url": p.get("image_url"),
                "metadata": p,
                "source": "supabase_direct"
            }

        # --- Step 2: Semantic Translation fallback (Supabase pgvector) ---
        logger.debug(f"No direct match for '{name}', using Supabase semantic fallback...")
        fallback = search_products(name, top_k=1, match_threshold=0.5)
        
        if fallback:
            top_match = fallback[0]
            match_name = top_match.get("name")
            score = top_match.get("score")
            
            # Use confidence threshold (0.5 for BGE models)
            if score and score > 0.5:
                logger.info(f"Supabase translated '{name}' -> '{match_name}' (score: {score:.2f})")
                return {
                    "found": True,
                    "name": top_match.get("name"),
                    "price": top_match.get("price"),
                    "image_url": top_match.get("image_url"),
                    "metadata": top_match.get("metadata"),
                    "score": score,
                    "source": "supabase_semantic"
                }

        logger.warning(f"Product '{name}' not found locally or via pgvector.")
        return {"found": False, "query": name}

    except Exception as e:
        logger.error(f"get_product_by_name (supabase hybrid) failed for '{name}': {str(e)}")
        return {"found": False, "query": name, "error": str(e)}
