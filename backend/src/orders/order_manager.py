from datetime import datetime
from typing import List, Optional
import logging

from src.graph.state import ProductItem
from src.memory.supabase_client import supabase_admin as supabase

logger = logging.getLogger(__name__)

TABLE = "coffee_shop_orders"


def get_active_order(user_email: str) -> tuple[List[ProductItem], float]:
    """Load the user's active pending order. Returns ([], 0.0) if none."""
    try:
        res = (
            supabase.table(TABLE)
            .select("*")
            .eq("user_email", user_email)
            .eq("status", "pending")
            .order("updated_at", desc=True)
            .limit(1)
            .execute()
        )
        if not res.data:
            return [], 0.0

        row = res.data[0]
        items = [ProductItem(**i) for i in row.get("items", [])]
        total = float(row.get("total", 0.0))
        return items, total

    except Exception as e:
        logger.error(f"get_active_order failed for {user_email}: {e}")
        return [], 0.0


def save_order(user_email: str, items: List[ProductItem], total: float) -> None:
    """Replace the active pending order for this user."""
    try:
        supabase.table(TABLE).delete().eq("user_email", user_email).eq("status", "pending").execute()

        if not items:
            return

        data = {
            "user_email": user_email,
            "items": [i.model_dump() for i in items],
            "total": total,
            "status": "pending",
            "updated_at": datetime.now().isoformat(),
        }
        supabase.table(TABLE).insert(data).execute()
        logger.info(f"Order saved for {user_email} — {len(items)} items, ₹{total}")

    except Exception as e:
        logger.error(f"save_order failed for {user_email}: {e}")


def confirm_order(user_email: str, items: List[ProductItem], total: float) -> Optional[str]:
    """Confirm the order — delete pending, insert confirmed. Returns order_id."""
    try:
        supabase.table(TABLE).delete().eq("user_email", user_email).eq("status", "pending").execute()

        data = {
            "user_email": user_email,
            "items": [i.model_dump() for i in items],
            "total": total,
            "status": "confirmed",
            "updated_at": datetime.now().isoformat(),
        }
        res = supabase.table(TABLE).insert(data).execute()
        order_id = res.data[0]["id"] if res.data else None
        logger.info(f"Order confirmed for {user_email}, order_id={order_id}")
        return order_id

    except Exception as e:
        logger.error(f"confirm_order failed for {user_email}: {e}")
        return None


def cancel_order(user_email: str) -> None:
    """Hard delete the pending order for this user."""
    try:
        supabase.table(TABLE).delete().eq("user_email", user_email).eq("status", "pending").execute()
        logger.info(f"Pending order cancelled for {user_email}")
    except Exception as e:
        logger.error(f"cancel_order failed for {user_email}: {e}")
