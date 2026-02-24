"""Product info tool — fetch price, rating, availability for specific items."""

import logging
from typing import List
from langchain_core.tools import StructuredTool
from src.tools.schemas import ProductInfoInput, ProductInfoOutput, ProductItem
from src.rag.retriever import get_product_by_name

logger = logging.getLogger(__name__)


def get_product_info_func(product_names: List[str]) -> str:
    """Fetch detailed info for one or more products by exact name."""
    try:
        logger.info(f"Fetching product info for: {product_names}")
        lines = []

        for name in product_names:
            result = get_product_by_name(name)

            if result.get("found"):
                meta = result.get("metadata", {})
                price       = result.get("price") or meta.get("price", 0.0)
                rating      = meta.get("rating", "N/A")
                category    = meta.get("category", "")
                ingredients = meta.get("ingredients", "")
                available   = meta.get("is_available", True)

                line = f"**{result.get('name', name)}** — ₹{price:.2f}, rated {rating}/5"
                if category:
                    line += f", category: {category}"
                if ingredients:
                    line += f"\n   Ingredients: {ingredients}"
                if not available:
                    line += " *(currently unavailable)*"
                lines.append(line)
            else:
                lines.append(f"**{name}** — not found in our menu.")

        return "\n".join(lines)

    except Exception as e:
        logger.error(f"get_product_info_func failed: {str(e)}")
        return "Sorry, I couldn't retrieve product info right now. Please try again."


product_info_tool = StructuredTool.from_function(
    name="GetProductInfoTool",
    func=get_product_info_func,
    description=(
        "Get detailed product info (price, rating, availability, ingredients) for specific items. "
        "Use when the user asks about a specific product by name. "
        "Input is a list of product names e.g. ['Cappuccino', 'Latte']."
    ),
    args_schema=ProductInfoInput,
)
