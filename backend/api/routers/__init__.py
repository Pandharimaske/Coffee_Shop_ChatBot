from api.routers.auth import router as auth_router
from api.routers.users import router as users_router
from api.routers.chat import router as chat_router
from api.routers.orders import router as orders_router
from api.routers.products import router as products_router

__all__ = [
    "auth_router",
    "users_router",
    "chat_router",
    "orders_router",
    "products_router",
]
