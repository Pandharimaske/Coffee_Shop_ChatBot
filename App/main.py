from fastapi import FastAPI, Request
from App.schemas import ChatRequest, ChatResponse
from App.chatbot import get_bot_response
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from dotenv import load_dotenv
load_dotenv()

# Load Telegram token (set this in Render environment variables)
TELEGRAM_API_URL = f"https://api.telegram.org/bot{os.getenv("TELEGRAM_TOKEN")}"

app = FastAPI(title="Coffee Shop Bot API")

# CORS setup (for frontend use)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health & base routes
@app.get("/")
def root():
    return {"message": "Coffee Bot API is live!"}

@app.get("/health")
def health():
    return {"status": "ok"}

# Main chat endpoint (used by web frontend or testing)
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    result = get_bot_response(request.user_input, request.user_id)
    return ChatResponse(**result)

# 🔁 Telegram webhook route
@app.post("/telegram-webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    message = data.get("message", {}).get("text")
    chat_id = data.get("message", {}).get("chat", {}).get("id")

    if not message or not chat_id:
        return {"ok": True}

    # Directly use your bot logic
    result = get_bot_response(message, chat_id)
    bot_reply = result.get("response", "Sorry, something went wrong.")

    # Send reply to Telegram
    async with httpx.AsyncClient() as client:
        await client.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": bot_reply
        })

    return {"ok": True}
