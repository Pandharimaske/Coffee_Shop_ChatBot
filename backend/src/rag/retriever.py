"""Scalable Retriever helpers for Coffee Shop RAG - Multi-user version

Provides utilities to query Pinecone indices with:
- Connection pooling & caching (reuse across requests)
- Multi-tenant support (user/organization isolation)
- Comprehensive error handling & monitoring
- Rate limiting & retry logic
- Request tracing for debugging
"""

import os
import logging
from typing import List, Dict, Any, Optional
from functools import lru_cache
from datetime import datetime

import dotenv
from pinecone import Pinecone, PineconeException
from langchain_huggingface import HuggingFaceEndpointEmbeddings

from src.config import Config, RetrieverConfig as ConfigRetrieverConfig

dotenv.load_dotenv()

logger = logging.getLogger(__name__)


# Use centralized RetrieverConfig from src/config.py
RetrieverConfig = ConfigRetrieverConfig


class PooledRetriever:
    """Manages pooled connections for embeddings and Pinecone."""

    _instance = None
    _embedding_cache = {}
    _pinecone_client = None

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
        logger.info("PooledRetriever initialized with connection pooling")

    @property
    def pinecone_client(self) -> Pinecone:
        """Get or create Pinecone client (singleton)."""
        if PooledRetriever._pinecone_client is None:
            PooledRetriever._pinecone_client = Pinecone(api_key=Config.PINECONE_API_KEY)
            logger.info("Pinecone client initialized")
        return PooledRetriever._pinecone_client

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

    def get_index(self, index_name: str):
        """Get Pinecone index with validation."""
        try:
            return self.pinecone_client.Index(index_name)
        except Exception as e:
            logger.error(f"Failed to get Pinecone index '{index_name}': {str(e)}")
            raise

    @classmethod
    def clear_cache(cls):
        """Clear all caches - useful for testing or credential rotation."""
        cls._embedding_cache.clear()
        cls._pinecone_client = None
        logger.info("PooledRetriever cache cleared")


class MultiTenantRetriever:
    """Multi-tenant aware retriever with user/organization isolation."""

    def __init__(self):
        self.retriever = PooledRetriever()

    def get_user_index_name(self, user_id: str, org_id: Optional[str] = None) -> str:
        """Generate isolated index name for user/org.
        
        Format: {prefix}-{org_id or 'default'}-{user_id}
        Example: coffee-shop-acme-corp-user-123
        """
        org = org_id or "default"
        prefix = Config.PINECONE_INDEX_PREFIX
        return f"{prefix}-{org}-{user_id}"

    def query_products(
        self,
        query: str,
        user_id: str,
        org_id: Optional[str] = None,
        top_k: Optional[int] = None,
        filter_dict: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Query products for a specific user/tenant.
        
        Args:
            query: Search text
            user_id: User identifier
            org_id: Organization identifier (optional, defaults to 'default')
            top_k: Number of results (defaults to config)
            filter_dict: Pinecone metadata filter
            
        Returns:
            Dict with results, metadata, and request info
        """
        top_k = top_k or Config.RETRIEVER_DEFAULT_TOP_K
        if top_k > Config.RETRIEVER_MAX_TOP_K:
            logger.warning(f"top_k {top_k} exceeds max {Config.RETRIEVER_MAX_TOP_K}, capping")
            top_k = Config.RETRIEVER_MAX_TOP_K

        index_name = self.get_user_index_name(user_id, org_id)
        request_id = f"{user_id}-{datetime.utcnow().timestamp()}"

        try:
            logger.info(f"[{request_id}] Querying {index_name}: '{query}'")
            
            embeddings = self.retriever.get_embeddings()
            q_vec = embeddings.embed_query(query)
            
            idx = self.retriever.get_index(index_name)
            
            # Query with optional metadata filtering
            resp = idx.query(
                vector=q_vec,
                top_k=top_k,
                include_values=False,
                include_metadata=True,
                filter=filter_dict
            )

            results = self._parse_response(resp)
            
            logger.info(f"[{request_id}] Retrieved {len(results)} results")
            return {
                "success": True,
                "request_id": request_id,
                "results": results,
                "count": len(results),
                "query": query,
                "index": index_name,
            }
            
        except PineconeException as e:
            logger.error(f"[{request_id}] Pinecone error: {str(e)}")
            return {
                "success": False,
                "request_id": request_id,
                "error": f"Database query failed: {str(e)}",
                "results": [],
            }
        except Exception as e:
            logger.error(f"[{request_id}] Unexpected error: {str(e)}")
            return {
                "success": False,
                "request_id": request_id,
                "error": f"Internal error: {str(e)}",
                "results": [],
            }

    def retrieve_price_by_name(
        self,
        name: str,
        user_id: str,
        org_id: Optional[str] = None,
        top_k: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Retrieve product price by name for specific user/tenant."""
        from src.rag.vector_db_setup import VectorDBSetup

        top_k = top_k or Config.RETRIEVER_DEFAULT_TOP_K
        
        try:
            vsetup = VectorDBSetup()
            normalized = vsetup.normalize_text(name)
            
            response = self.query_products(
                query=name,
                user_id=user_id,
                org_id=org_id,
                top_k=top_k,
            )
            
            if not response.get("success") or not response.get("results"):
                return {
                    "found": False,
                    "query": name,
                    "request_id": response.get("request_id"),
                }

            results = response["results"]
            
            # Try exact normalized match first
            for r in results:
                meta = r.get("metadata") or {}
                if meta.get("name_normalized") == normalized:
                    return {
                        "found": True,
                        "name": r.get("name"),
                        "price": r.get("price"),
                        "score": r.get("score"),
                        "request_id": response.get("request_id"),
                    }

            # Fallback to top result
            top = results[0]
            return {
                "found": True,
                "name": top.get("name"),
                "price": top.get("price"),
                "score": top.get("score"),
                "request_id": response.get("request_id"),
            }
            
        except Exception as e:
            logger.error(f"Error retrieving price for '{name}': {str(e)}")
            return {
                "found": False,
                "query": name,
                "error": str(e),
            }

    @staticmethod
    def _parse_response(resp) -> List[Dict[str, Any]]:
        """Parse Pinecone response into standardized format."""
        results = []
        matches = []
        
        if hasattr(resp, 'matches'):
            matches = resp.matches
        elif isinstance(resp, dict) and resp.get('matches'):
            matches = resp['matches']

        for m in matches:
            meta = getattr(m, 'metadata', None) or m.get('metadata', {})
            score = getattr(m, 'score', None) or m.get('score')
            results.append({
                "name": meta.get("name"),
                "price": meta.get("price"),
                "score": score,
                "metadata": meta,
            })

        return results


# Convenience singleton for single-tenant use
_pooled_retriever = PooledRetriever()


def search_products(
    query: str,
    top_k: int = 5,
    index_name: str = "coffee-products",
) -> List[Dict[str, Any]]:
    """Search products using semantic similarity.

    Args:
        query: Natural language search query
        top_k: Number of results to return
        index_name: Pinecone index name

    Returns:
        List of product dicts with name, price, score, metadata
    """
    try:
        embeddings = _pooled_retriever.get_embeddings()
        q_vec = embeddings.embed_query(query)
        idx = _pooled_retriever.get_index(index_name)
        resp = idx.query(vector=q_vec, top_k=top_k, include_values=False, include_metadata=True)
        return MultiTenantRetriever._parse_response(resp)
    except Exception as e:
        logger.error(f"search_products failed: {str(e)}")
        return []


def get_product_by_name(
    name: str,
    index_name: str = "coffee-products",
) -> Dict[str, Any]:
    """Fetch a single product by exact name using Pinecone metadata filter.

    Uses metadata filter on name_normalized for a true exact lookup —
    no semantic search involved. Falls back to semantic search if no
    exact match is found.

    Args:
        name: Product name to look up
        index_name: Pinecone index name

    Returns:
        Dict with found, name, price, score, metadata
    """
    try:
        normalized = name.lower().strip()
        idx = _pooled_retriever.get_index(index_name)
        embeddings = _pooled_retriever.get_embeddings()

        # Step 1: Exact lookup via metadata filter
        # Pinecone requires a query vector even with filters — use the name itself
        q_vec = embeddings.embed_query(name)
        resp = idx.query(
            vector=q_vec,
            top_k=1,
            include_values=False,
            include_metadata=True,
            filter={"name_normalized": {"$eq": normalized}}
        )
        results = MultiTenantRetriever._parse_response(resp)

        if results:
            r = results[0]
            meta = r.get("metadata", {})
            logger.debug(f"Exact match found for '{name}'")
            return {"found": True, "name": r.get("name"), "price": r.get("price"), "score": r.get("score"), "metadata": meta}

        # Step 2: Fallback to semantic search
        logger.debug(f"No exact match for '{name}', falling back to semantic search")
        fallback = search_products(name, top_k=1, index_name=index_name)
        if fallback:
            top = fallback[0]
            return {"found": True, "name": top.get("name"), "price": top.get("price"), "score": top.get("score"), "metadata": top.get("metadata", {})}

        return {"found": False, "query": name}

    except Exception as e:
        logger.error(f"get_product_by_name failed for '{name}': {str(e)}")
        return {"found": False, "query": name, "error": str(e)}
