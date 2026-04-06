from fastapi import APIRouter, HTTPException, status
from api.auth import CurrentUser
from api.schemas import UserResponse, PreferencesRequest, PreferencesResponse
from src.memory.memory_manager import get_user_memory, save_user_memory
from src.memory.schemas import UserMemory

router = APIRouter(prefix="/user", tags=["user"])


from src.memory.supabase_client import supabase

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: CurrentUser):
    # Fetch is_admin from profiles
    is_admin = False
    try:
        res = supabase.table("coffee_shop_profiles").select("is_admin").eq("user_email", current_user.email).execute()
        if res.data and res.data[0].get("is_admin"):
            is_admin = True
    except Exception:
        pass
        
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        is_admin=is_admin,
    )


@router.get("/preferences", response_model=PreferencesResponse)
async def get_preferences(current_user: CurrentUser):
    memory = get_user_memory(current_user.email)
    return PreferencesResponse(**memory.model_dump())


@router.put("/preferences", response_model=PreferencesResponse)
async def update_preferences(body: PreferencesRequest, current_user: CurrentUser):
    """
    Onboarding / settings form endpoint.
    Merges updates into existing preferences to avoid wiping feedback/history.
    """
    # 1. Fetch existing memory to perform a Smart Merge
    existing_memory = get_user_memory(current_user.email)
    
    # 2. Update only the fields provided in the body
    existing_memory.name = body.name
    existing_memory.likes = body.likes if body.likes is not None else existing_memory.likes
    existing_memory.dislikes = body.dislikes if body.dislikes is not None else existing_memory.dislikes
    existing_memory.allergies = body.allergies if body.allergies is not None else existing_memory.allergies
    existing_memory.location = body.location
    
    # NOTE: feedback and last_order are preserved because they are already in existing_memory
    
    # 3. Save the merged memory
    save_user_memory(current_user.email, existing_memory)
    
    return PreferencesResponse(**existing_memory.model_dump())
