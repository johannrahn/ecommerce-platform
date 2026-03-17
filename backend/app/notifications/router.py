from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies import DBSession, get_current_user
from app.notifications import service
from app.notifications.schemas import NotificationResponse
from app.users.models import User

router = APIRouter(prefix="/notifications", tags=["notifications"])

CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get("", response_model=list[NotificationResponse], summary="List my notifications")
def list_notifications(current_user: CurrentUser, db: DBSession):
    return service.get_user_notifications(db, current_user.id)


@router.post(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    summary="Mark notification as read",
)
def mark_read(notification_id: str, current_user: CurrentUser, db: DBSession):
    return service.mark_as_read(db, current_user.id, notification_id)


@router.post("/read-all", summary="Mark all notifications as read")
def mark_all_read(current_user: CurrentUser, db: DBSession):
    count = service.mark_all_as_read(db, current_user.id)
    return {"marked_read": count}
