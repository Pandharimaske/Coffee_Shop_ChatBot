import uuid
from fastapi import APIRouter, HTTPException
from api.auth import CurrentUser
from api.schemas import ChatRequest, ChatResponse, MessageHistoryResponse
from src.graph.graph import build_coffee_shop_graph
from src.graph.state import CoffeeAgentState
from src.memory.memory_manager import get_user_memory
from src.orders import get_active_order
from src.sessions import get_or_create_session, load_messages, save_messages

router = APIRouter(prefix="/chat", tags=["chat"])

_graph = build_coffee_shop_graph()


@router.get("/history", response_model=list[MessageHistoryResponse])
async def get_history(session_id: str, current_user: CurrentUser):
    """Load message history for a session — called on page load/refresh."""
    messages = load_messages(session_id)
    return [
        MessageHistoryResponse(
            role="user" if m.__class__.__name__ == "HumanMessage" else "assistant",
            content=m.content,
        )
        for m in messages
    ]


@router.post("", response_model=ChatResponse)
async def chat(body: ChatRequest, current_user: CurrentUser):
    user_email = current_user.email
    session_id = body.session_id or str(uuid.uuid4())

    get_or_create_session(session_id, user_email)

    try:
        user_memory = get_user_memory(user_email)
    except Exception:
        user_memory = None

    try:
        order, final_price = get_active_order(user_email)
    except Exception:
        order, final_price = [], 0.0

    messages = load_messages(session_id)

    state = CoffeeAgentState(
        user_input=body.user_input,
        user_memory=user_memory or CoffeeAgentState().user_memory,
        order=order,
        final_price=final_price,
        messages=messages,
    )

    config = {
        "configurable": {
            "thread_id": session_id,
            "user_id": user_email,
        }
    }

    try:
        final_state = await _graph.ainvoke(state, config=config)
        response = (
            final_state.get("response_message")
            if isinstance(final_state, dict)
            else final_state.response_message
        ) or "Sorry, I had a little trouble with that. Could you try again?"

        save_messages(session_id, user_email, body.user_input, response)

        return ChatResponse(session_id=session_id, response=response)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chatbot error: {str(e)}")
