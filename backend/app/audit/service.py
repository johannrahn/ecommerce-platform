import json
import logging
from datetime import datetime

from sqlalchemy.orm import Session

from app.audit.models import AuditLog

logger = logging.getLogger(__name__)


def create_audit_log(
    db: Session,
    admin_user_id: str,
    action: str,
    entity_type: str,
    entity_id: str,
    metadata: dict | None = None,
) -> AuditLog:
    """Create an audit log record. Called from other services within a transaction."""
    entry = AuditLog(
        admin_user_id=admin_user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        metadata_json=json.dumps(metadata) if metadata else None,
    )
    db.add(entry)
    return entry


def get_audit_logs(
    db: Session,
    action: str | None = None,
    entity_type: str | None = None,
    admin_user_id: str | None = None,
    created_after: datetime | None = None,
    created_before: datetime | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict:
    query = db.query(AuditLog)

    if action:
        query = query.filter(AuditLog.action == action)
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if admin_user_id:
        query = query.filter(AuditLog.admin_user_id == admin_user_id)
    if created_after:
        query = query.filter(AuditLog.created_at >= created_after)
    if created_before:
        query = query.filter(AuditLog.created_at <= created_before)

    total = query.count()
    items = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()

    return {
        "items": [_format_audit_log(a) for a in items],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


def _format_audit_log(entry: AuditLog) -> dict:
    return {
        "id": entry.id,
        "admin_user_id": entry.admin_user_id,
        "action": entry.action,
        "entity_type": entry.entity_type,
        "entity_id": entry.entity_id,
        "metadata_json": entry.metadata_json,
        "created_at": entry.created_at,
    }
