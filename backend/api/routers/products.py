import json
import logging
import os
from fastapi import APIRouter, Query
from typing import Optional
from api.schemas import ProductResponse
from src.memory.supabase_client import supabase_admin as supabase

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/products", tags=["products"])

# Local fallback — used when Supabase is unreachable
_LOCAL_PRODUCTS_PATH = os.path.join(
    os.path.dirname(__file__), "../../data/products_data/products.jsonl"
)

def _load_local_products() -> list[dict]:
    """Load products from local JSONL file as fallback."""
    products = []
    try:
        with open(_LOCAL_PRODUCTS_PATH, "r") as f:
            for i, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                products.append({
                    "id": i + 1,
                    "name": data["name"],
                    "category": data.get("category"),
                    "description": data.get("description"),
                    "price": float(data["price"]),
                    "rating": float(data["rating"]) if data.get("rating") else None,
                    "ingredients": data.get("ingredients", []),
                    "image_url": f"/images/{data['image_path']}" if data.get("image_path") else None,
                })
        logger.info(f"Loaded {len(products)} products from local fallback")
    except Exception as e:
        logger.error(f"Local product fallback failed: {e}")
    return products


@router.get("", response_model=list[ProductResponse])
async def get_products(
    category: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
):
    # Try Supabase first
    try:
        query = supabase.table("coffee_shop_products").select("*")
        if category:
            query = query.eq("category", category)
        if search:
            query = query.ilike("name", f"%{search}%")
        res = query.order("name").execute()

        if res.data:
            logger.info(f"Products from Supabase: {len(res.data)} rows")
            return [ProductResponse(**row) for row in res.data]

    except Exception as e:
        logger.warning(f"Supabase products unavailable ({e}) — using local fallback")

    # Fallback to local JSONL
    products = _load_local_products()

    if category:
        products = [p for p in products if p.get("category", "").lower() == category.lower()]
    if search:
        products = [p for p in products if search.lower() in p["name"].lower()]

    return [ProductResponse(**p) for p in sorted(products, key=lambda x: x["name"])]
