from fastapi import APIRouter, HTTPException, status
from api.auth import auth
from api.schemas import RegisterRequest, LoginRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest):
    try:
        user = await auth.register(
            email=body.email,
            password=body.password,
            username=body.username,
        )
        return UserResponse(id=user.id, email=user.email, username=user.username)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest):
    try:
        tokens = await auth.login(email=body.email, password=body.password)
        return TokenResponse(access_token=tokens.access_token, token_type=tokens.token_type)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
