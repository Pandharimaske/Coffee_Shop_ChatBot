import logging
from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from api.schemas import ProductResponse
from src.memory.supabase_client import supabase_admin as supabase

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[ProductResponse])
async def get_products(
    category: Optional[str] = Query(default=None, description="Filter by category"),
    search: Optional[str] = Query(default=None, description="Search by name"),
):
    try:
        query = supabase.table("coffee_shop_products").select("*")

        if category:
            query = query.eq("category", category)

        if search:
            query = query.ilike("name", f"%{search}%")

        res = query.order("name").execute()
        logger.info(f"Products query returned {len(res.data or [])} rows")
        return [ProductResponse(**row) for row in (res.data or [])]

    except Exception as e:
        logger.error(f"get_products failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
