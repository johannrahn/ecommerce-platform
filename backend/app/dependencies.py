from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.exceptions import ForbiddenError, UnauthorizedError


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DBSession = Annotated[Session, Depends(get_db)]


def _get_token_from_header(
    authorization: Annotated[str | None, Header()] = None,
) -> str:
    """Extract Bearer token from Authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedError()
    return authorization.removeprefix("Bearer ")


def get_current_user(
    db: DBSession,
    token: Annotated[str, Depends(_get_token_from_header)],
):
    """Decode JWT and return the current user. Raises 401 if invalid."""
    from app.auth.security import decode_access_token
    from app.users.models import User

    payload = decode_access_token(token)
    if payload is None:
        raise UnauthorizedError()

    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise UnauthorizedError()

    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        raise UnauthorizedError()

    return user


def require_admin(
    db: DBSession,
    token: Annotated[str, Depends(_get_token_from_header)],
):
    """Dependency that ensures the current user is an admin."""
    from app.users.models import UserRole

    user = get_current_user(db, token)
    if user.role != UserRole.ADMIN:
        raise ForbiddenError()
    return user
