from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.audit import service
from app.audit.schemas import PaginatedAuditLogs
from app.dependencies import DBSession, require_admin
from app.users.models import User

router = APIRouter(prefix="/admin/audit-logs", tags=["admin-audit"])

AdminUser = Annotated[User, Depends(require_admin)]


@router.get("", response_model=PaginatedAuditLogs, summary="List audit logs")
def list_audit_logs(
    admin: AdminUser,
    db: DBSession,
    action: str | None = None,
    entity_type: str | None = None,
    admin_user_id: str | None = None,
    created_after: datetime | None = None,
    created_before: datetime | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return service.get_audit_logs(
        db,
        action=action,
        entity_type=entity_type,
        admin_user_id=admin_user_id,
        created_after=created_after,
        created_before=created_before,
        limit=limit,
        offset=offset,
    )
