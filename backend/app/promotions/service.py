import logging
from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.audit.service import create_audit_log
from app.exceptions import AppException, ConflictError, NotFoundError
from app.promotions.models import Coupon, CouponUsage, DiscountType

logger = logging.getLogger(__name__)


# ── Admin CRUD ──────────────────────────────────────────────


def create_coupon(db: Session, data: dict, admin_user_id: str | None = None) -> dict:
    # Normalize code to uppercase for case-insensitive uniqueness
    data["code"] = data["code"].upper()

    if db.query(Coupon).filter(func.upper(Coupon.code) == data["code"]).first():
        raise ConflictError(f"Coupon code '{data['code']}' already exists")

    coupon = Coupon(**data)
    db.add(coupon)
    db.flush()

    if admin_user_id:
        create_audit_log(
            db, admin_user_id, "coupon.created",
            entity_type="coupon", entity_id=coupon.id,
            metadata={"code": coupon.code, "discount_type": coupon.discount_type.value},
        )

    db.commit()
    db.refresh(coupon)
    logger.info("coupon.created code=%s id=%s", coupon.code, coupon.id)
    return _format_coupon(coupon)


def list_coupons(db: Session, include_inactive: bool = True) -> list[dict]:
    query = db.query(Coupon)
    if not include_inactive:
        query = query.filter(Coupon.is_active.is_(True))
    coupons = query.order_by(Coupon.created_at.desc()).all()
    return [_format_coupon(c) for c in coupons]


def get_coupon(db: Session, coupon_id: str) -> dict:
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if coupon is None:
        raise NotFoundError("Coupon not found")
    return _format_coupon(coupon)


def update_coupon(
    db: Session, coupon_id: str, data: dict, admin_user_id: str | None = None
) -> dict:
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if coupon is None:
        raise NotFoundError("Coupon not found")

    if "code" in data:
        data["code"] = data["code"].upper()
        if data["code"] != coupon.code:
            existing = db.query(Coupon).filter(func.upper(Coupon.code) == data["code"]).first()
            if existing:
                raise ConflictError(f"Coupon code '{data['code']}' already exists")

    old_active = coupon.is_active

    for key, value in data.items():
        setattr(coupon, key, value)

    if admin_user_id:
        action = "coupon.updated"
        if "is_active" in data and data["is_active"] != old_active:
            action = "coupon.activated" if data["is_active"] else "coupon.deactivated"
        create_audit_log(
            db, admin_user_id, action,
            entity_type="coupon", entity_id=coupon.id,
            metadata={"changes": list(data.keys())},
        )

    db.commit()
    db.refresh(coupon)
    logger.info("coupon.updated id=%s code=%s", coupon.id, coupon.code)
    return _format_coupon(coupon)


# ── Validation ──────────────────────────────────────────────


def validate_coupon(
    db: Session, code: str, user_id: str, subtotal: float | None = None
) -> Coupon:
    """Validate a coupon code and return the Coupon object.

    When subtotal is None (cart apply), minimum_order_amount is not checked.
    When subtotal is provided (checkout), all checks including minimum are applied.
    """
    coupon = (
        db.query(Coupon).filter(func.upper(Coupon.code) == code.upper()).first()
    )
    if coupon is None:
        raise AppException(status_code=404, detail="Coupon not found")

    if not coupon.is_active:
        raise AppException(status_code=400, detail="Coupon is not active")

    now = datetime.now(timezone.utc)
    if coupon.starts_at:
        starts = coupon.starts_at if coupon.starts_at.tzinfo else coupon.starts_at.replace(tzinfo=timezone.utc)
        if now < starts:
            raise AppException(status_code=400, detail="Coupon is not yet valid")
    if coupon.ends_at:
        ends = coupon.ends_at if coupon.ends_at.tzinfo else coupon.ends_at.replace(tzinfo=timezone.utc)
        if now > ends:
            raise AppException(status_code=400, detail="Coupon has expired")

    if coupon.max_uses is not None and coupon.used_count >= coupon.max_uses:
        raise AppException(status_code=400, detail="Coupon usage limit reached")

    if subtotal is not None and coupon.minimum_order_amount is not None:
        if subtotal < float(coupon.minimum_order_amount):
            raise AppException(
                status_code=400,
                detail=(
                    f"Order subtotal ({subtotal:.2f}) does not meet "
                    f"minimum amount ({float(coupon.minimum_order_amount):.2f})"
                ),
            )

    if coupon.one_per_user:
        already_used = (
            db.query(CouponUsage)
            .filter(
                CouponUsage.coupon_id == coupon.id,
                CouponUsage.user_id == user_id,
            )
            .first()
        )
        if already_used:
            raise AppException(
                status_code=400, detail="You have already used this coupon"
            )

    return coupon


def calculate_discount(coupon: Coupon, subtotal: float) -> float:
    """Calculate the discount amount. Applies max_discount_amount cap. Never exceeds subtotal."""
    if coupon.discount_type == DiscountType.PERCENT:
        discount = round(subtotal * float(coupon.discount_value) / 100, 2)
        # Apply max discount cap for percentage coupons
        if coupon.max_discount_amount is not None:
            discount = min(discount, float(coupon.max_discount_amount))
    else:
        discount = float(coupon.discount_value)

    # Never let discount exceed subtotal (no negative totals)
    return min(discount, subtotal)


def record_usage(
    db: Session, coupon: Coupon, user_id: str, order_id: str
) -> None:
    """Increment used_count and record per-user usage."""
    coupon.used_count += 1
    if coupon.one_per_user:
        usage = CouponUsage(
            coupon_id=coupon.id, user_id=user_id, order_id=order_id
        )
        db.add(usage)


# ── Helpers ─────────────────────────────────────────────────


def _format_coupon(coupon: Coupon) -> dict:
    return {
        "id": coupon.id,
        "code": coupon.code,
        "description": coupon.description,
        "discount_type": coupon.discount_type,
        "discount_value": float(coupon.discount_value),
        "minimum_order_amount": (
            float(coupon.minimum_order_amount)
            if coupon.minimum_order_amount is not None
            else None
        ),
        "max_discount_amount": (
            float(coupon.max_discount_amount)
            if coupon.max_discount_amount is not None
            else None
        ),
        "max_uses": coupon.max_uses,
        "used_count": coupon.used_count,
        "is_active": coupon.is_active,
        "starts_at": coupon.starts_at,
        "ends_at": coupon.ends_at,
        "one_per_user": coupon.one_per_user,
        "created_at": coupon.created_at,
        "updated_at": coupon.updated_at,
    }
