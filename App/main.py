# App/main.py

from fastapi import FastAPI
from App.schemas import ChatRequest, ChatResponse
from App.chatbot import get_bot_response
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Coffee Shop Bot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Coffee Bot API is live!"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    result = get_bot_response(request.user_input, request.user_id, request.state)
    return ChatResponse(**result)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("App.main:app", host="127.0.0.1", port=8000, reload=True)