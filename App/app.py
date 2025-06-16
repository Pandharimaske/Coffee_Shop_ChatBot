from fastapi import FastAPI
from App.schemas import ChatRequest , ChatResponse
from App.chatbot import get_bot_response

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Coffee Bot API is live!"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    response = get_bot_response(request.message)
    return ChatResponse(response=response)



"""uvicorn App.app:app --reload"""