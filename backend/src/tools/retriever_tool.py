"""RAG-based product search tool for the Coffee Shop."""

import logging
from langchain_core.tools import StructuredTool
from src.tools.schemas import ProductQueryInput
from src.rag.retriever import search_products

logger = logging.getLogger(__name__)


def rag_tool_func(query: str, top_k: int = 5) -> str:
    """Search for products using semantic similarity and return formatted results."""
    try:
        logger.info(f"Searching products: '{query}' (top_k={top_k})")
        products = search_products(query, top_k=top_k)

        if not products:
            return "No matching products found in our menu."

        lines = []
        for i, p in enumerate(products, 1):
            meta = p.get("metadata", {})
            name        = p.get("name") or meta.get("name", "Unknown")
            price       = p.get("price") or meta.get("price", 0.0)
            rating      = meta.get("rating", "N/A")
            description = meta.get("description") or meta.get("text", "")
            ingredients = meta.get("ingredients", "")

            line = f"**{i}. {name}** — ₹{price:.2f}, rated {rating}/5"
            if description:
                line += f"\n   {description}"
            if ingredients:
                line += f"\n   Ingredients: {ingredients}"
            lines.append(line)

        return "\n".join(lines)

    except Exception as e:
        logger.error(f"rag_tool_func failed: {str(e)}")
        return "Sorry, I couldn't search the menu right now. Please try again."


rag_tool = StructuredTool.from_function(
    name="CoffeeShopProductRetriever",
    func=rag_tool_func,
    description=(
        "Search for coffee shop products and menu items by natural language query. "
        "Use for browsing the menu, finding items by category, ingredients, or description. "
        "Returns name, price, rating, description, and ingredients."
    ),
    args_schema=ProductQueryInput,
)
