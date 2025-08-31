from fastapi import FastAPI, Request
from App.schemas import ChatRequest, ChatResponse
from App.chatbot import get_bot_response
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from dotenv import load_dotenv
load_dotenv()

# Load Telegram token (set this in Render environment variables)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "your_telegram_bot_token_here")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

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
# @app.post("/chat", response_model=ChatResponse)
# def chat(request: ChatRequest):
#     state = get_bot_response(request.user_input, request.user_id)
#     result = {
#             "response": state.get("response_message", "Sorry, I can't help with that."),
#             "state": state
#         }
#     return ChatResponse(**result)

from fastapi.responses import StreamingResponse
from Backend.nodes.response_node import ResponseNode

response_node = ResponseNode()

@app.get("/chat/stream")
async def chat_stream(user_input: str, user_id: str):
    async def event_generator():
        # Get agent state using your existing helper
        state = get_bot_response(user_input, user_id)

        async for chunk in response_node.astream(
            state,
            config={"configurable": {"user_id": user_id}},
        ):
            yield f"data: {chunk}\n\n"

        # Indicate end of stream
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )


# 🔁 Telegram webhook route
@app.post("/telegram-webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    message = data.get("message", {}).get("text")
    chat_id = data.get("message", {}).get("chat", {}).get("id")

    print("Telegram message: " , message)
    print("Telegram chat_id: " , chat_id)

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
