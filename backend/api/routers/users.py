from fastapi import APIRouter, HTTPException, status
from api.auth import CurrentUser
from api.schemas import UserResponse, PreferencesRequest, PreferencesResponse
from src.memory.memory_manager import get_user_memory, save_user_memory
from src.memory.schemas import UserMemory

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: CurrentUser):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
    )


@router.get("/preferences", response_model=PreferencesResponse)
async def get_preferences(current_user: CurrentUser):
    memory = get_user_memory(current_user.email)
    return PreferencesResponse(**memory.model_dump())


@router.put("/preferences", response_model=PreferencesResponse)
async def update_preferences(body: PreferencesRequest, current_user: CurrentUser):
    """
    Onboarding / settings form endpoint.
    Completely replaces preferences with what user submits.
    """
    memory = UserMemory(
        name=body.name,
        likes=body.likes or [],
        dislikes=body.dislikes or [],
        allergies=body.allergies or [],
        location=body.location,
        feedback=[],
        last_order=None,
    )
    save_user_memory(current_user.email, memory)
    return PreferencesResponse(**memory.model_dump())
