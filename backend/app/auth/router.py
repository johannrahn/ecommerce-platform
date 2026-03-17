from fastapi import APIRouter

from app.auth import service
from app.auth.schemas import LoginRequest, RegisterRequest, TokenResponse
from app.dependencies import DBSession
from app.users.schemas import UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201, summary="Register a new user")
def register(data: RegisterRequest, db: DBSession):
    return service.register_user(
        db,
        email=data.email,
        password=data.password,
        full_name=data.full_name,
    )


@router.post("/login", response_model=TokenResponse, summary="Login and get access token")
def login(data: LoginRequest, db: DBSession):
    token = service.authenticate_user(db, email=data.email, password=data.password)
    return TokenResponse(access_token=token)
