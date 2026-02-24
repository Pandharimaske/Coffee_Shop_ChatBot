from fastapi import APIRouter
from api.auth import CurrentUser
from api.schemas import ActiveOrderResponse, OrderHistoryResponse, UpdateOrderRequest, UpdateOrderItemRequest
from src.orders import get_active_order, save_order, cancel_order
from src.graph.state import ProductItem
from src.memory.supabase_client import supabase_admin as supabase

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/active", response_model=ActiveOrderResponse)
async def get_active(current_user: CurrentUser):
    items, total = get_active_order(current_user.email)
    return ActiveOrderResponse(
        items=[i.model_dump() for i in items],
        total=total,
    )


@router.put("/active", response_model=ActiveOrderResponse)
async def update_active(body: UpdateOrderRequest, current_user: CurrentUser):
    """
    Frontend calls this whenever cart changes.
    Completely replaces the active pending order with what frontend sends.
    """
    items = [
        ProductItem(
            name=item.name,
            quantity=item.quantity,
            per_unit_price=item.per_unit_price,
            total_price=round(item.per_unit_price * item.quantity, 2),
        )
        for item in body.items
    ]
    total = round(sum(i.total_price for i in items), 2)
    save_order(current_user.email, items, total)
    return ActiveOrderResponse(items=[i.model_dump() for i in items], total=total)


@router.delete("/active", status_code=204)
async def clear_active(current_user: CurrentUser):
    """Cancel/clear the active pending order."""
    cancel_order(current_user.email)


@router.get("/history", response_model=list[OrderHistoryResponse])
async def get_history(current_user: CurrentUser):
    try:
        res = (
            supabase.table("coffee_shop_orders")
            .select("*")
            .eq("user_email", current_user.email)
            .eq("status", "confirmed")
            .order("updated_at", desc=True)
            .execute()
        )
        return [
            OrderHistoryResponse(
                id=row["id"],
                items=row.get("items", []),
                total=row.get("total", 0.0),
                status=row["status"],
                updated_at=row["updated_at"],
            )
            for row in (res.data or [])
        ]
    except Exception:
        return []
