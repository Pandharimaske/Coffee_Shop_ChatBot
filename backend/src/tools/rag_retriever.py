"""Tool wrapper exposing RAG retrieval helpers for agents.

Agents can import these helpers to find products and prices.
This layer keeps agent code decoupled from Pinecone/langchain specifics.
"""
from typing import List, Dict, Any
import logging

from src.rag.retriever import query_products, retrieve_price_by_name

logger = logging.getLogger(__name__)


def find_products(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Return top-k product matches for a free-text query.
    
    Args:
        query: Free-text search query
        top_k: Number of results to retrieve (default: 5)
        
    Returns:
        List of product dictionaries with name, price, rating, etc.
    """
    try:
        logger.info(f"Finding products for: '{query}' (top_k={top_k})")
        results = query_products(query, top_k=top_k)
        logger.info(f"Found {len(results)} products")
        return results
    except Exception as e:
        logger.error(f"Error finding products: {str(e)}")
        return []


def find_price_for_item(name: str) -> Dict[str, Any]:
    """
    Return price information for a product name (approx match).
    
    Args:
        name: Product name to look up
        
    Returns:
        Dictionary with 'found', 'name', 'price', and 'score' keys
    """
    try:
        logger.info(f"Looking up price for: '{name}'")
        result = retrieve_price_by_name(name)
        logger.info(f"Found: {result.get('found', False)}")
        return result
    except Exception as e:
        logger.error(f"Error retrieving price for '{name}': {str(e)}")
        return {"found": False, "query": name, "error": str(e)}


if __name__ == "__main__":
    # quick manual test
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m src.tools.rag_retriever 'latte'")
    else:
        q = sys.argv[1]
        print(find_products(q))
