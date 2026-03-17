import logging

from sqlalchemy.orm import Session

from app.exceptions import NotFoundError
from app.notifications.models import Notification

logger = logging.getLogger(__name__)


def create_notification(
    db: Session,
    user_id: str,
    type: str,
    title: str,
    message: str,
) -> Notification:
    """Create a notification record. Called from other services within a transaction."""
    notification = Notification(
        user_id=user_id,
        type=type,
        title=title,
        message=message,
    )
    db.add(notification)
    return notification


def get_user_notifications(db: Session, user_id: str) -> list[dict]:
    notifications = (
        db.query(Notification)
        .filter(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .all()
    )
    return [_format_notification(n) for n in notifications]


def mark_as_read(db: Session, user_id: str, notification_id: str) -> dict:
    notification = (
        db.query(Notification)
        .filter(Notification.id == notification_id, Notification.user_id == user_id)
        .first()
    )
    if notification is None:
        raise NotFoundError("Notification not found")

    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return _format_notification(notification)


def mark_all_as_read(db: Session, user_id: str) -> int:
    count = (
        db.query(Notification)
        .filter(Notification.user_id == user_id, Notification.is_read.is_(False))
        .update({"is_read": True})
    )
    db.commit()
    return count


def _format_notification(notification: Notification) -> dict:
    return {
        "id": notification.id,
        "user_id": notification.user_id,
        "type": notification.type,
        "title": notification.title,
        "message": notification.message,
        "is_read": notification.is_read,
        "created_at": notification.created_at,
    }
