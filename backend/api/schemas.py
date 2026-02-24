from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional


# ── Auth ──────────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    email: str
    username: Optional[str] = None


# ── User / Preferences ────────────────────────────────────────────────────────

class PreferencesRequest(BaseModel):
    name: Optional[str] = None
    likes: Optional[List[str]] = []
    dislikes: Optional[List[str]] = []
    allergies: Optional[List[str]] = []
    location: Optional[str] = None


class PreferencesResponse(BaseModel):
    name: Optional[str] = None
    likes: List[str] = []
    dislikes: List[str] = []
    allergies: List[str] = []
    last_order: Optional[str] = None
    feedback: List[str] = []
    location: Optional[str] = None


# ── Chat ──────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    user_input: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    session_id: str
    response: str


class MessageHistoryResponse(BaseModel):
    role: str   # 'user' | 'assistant'
    content: str


# ── Orders ────────────────────────────────────────────────────────────────────

class OrderItemSchema(BaseModel):
    name: str
    quantity: int
    per_unit_price: Optional[float] = None
    total_price: Optional[float] = None


class UpdateOrderItemRequest(BaseModel):
    name: str
    quantity: int
    per_unit_price: float


class UpdateOrderRequest(BaseModel):
    items: List[UpdateOrderItemRequest]


class ActiveOrderResponse(BaseModel):
    items: List[OrderItemSchema]
    total: float


class OrderHistoryResponse(BaseModel):
    id: str
    items: List[OrderItemSchema]
    total: float
    status: str
    updated_at: str


# ── Products ──────────────────────────────────────────────────────────────────

class ProductResponse(BaseModel):
    id: str
    name: str
    category: Optional[str] = None
    description: Optional[str] = None
    price: float
    rating: Optional[float] = None
    ingredients: Optional[List[str]] = []
    image_url: Optional[str] = None
