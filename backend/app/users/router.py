from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies import DBSession, get_current_user, require_admin
from app.users import service
from app.users.models import User
from app.users.schemas import UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])

CurrentUser = Annotated[User, Depends(get_current_user)]
AdminUser = Annotated[User, Depends(require_admin)]


@router.get("/me", response_model=UserResponse, summary="Get my profile")
def get_my_profile(current_user: CurrentUser):
    return current_user


@router.put("/me", response_model=UserResponse, summary="Update my profile")
def update_my_profile(
    data: UserUpdate,
    current_user: CurrentUser,
    db: DBSession,
):
    return service.update_user(db, current_user, data.model_dump(exclude_unset=True))


@router.get("", response_model=list[UserResponse], summary="List all users (admin)")
def list_users(
    admin: AdminUser,
    db: DBSession,
    skip: int = 0,
    limit: int = 20,
):
    return service.get_users(db, skip=skip, limit=limit)
