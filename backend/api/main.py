import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import (
    auth_router,
    users_router,
    chat_router,
    orders_router,
    products_router,
)

app = FastAPI(
    title="Merry's Way Coffee Shop API",
    description="Backend API for Coffee Shop Chatbot",
    version="2.0.0",
)

# ── CORS ──────────────────────────────────────────────────────────────────────

# In production set ALLOWED_ORIGINS=https://your-app.vercel.app in Render env vars
# Multiple origins can be comma-separated: https://a.vercel.app,https://custom-domain.com
_raw_origins = os.getenv("ALLOWED_ORIGINS", "*")
ALLOWED_ORIGINS: list[str] = (
    ["*"] if _raw_origins.strip() == "*"
    else [o.strip() for o in _raw_origins.split(",") if o.strip()]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(chat_router)
app.include_router(orders_router)
app.include_router(products_router)


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "service": "Merry's Way Coffee Shop API"}


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
