import logging

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.audit.service import create_audit_log
from app.catalog.models import Product
from app.exceptions import AppException, ConflictError, ForbiddenError, NotFoundError
from app.notifications.service import create_notification
from app.orders.models import Order, OrderItem, OrderStatus
from app.reviews.models import Review

logger = logging.getLogger(__name__)


def create_review(db: Session, user_id: str, product_id: str, data: dict) -> dict:
    # Verify product exists
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise NotFoundError("Product not found")

    # Check duplicate
    existing = (
        db.query(Review)
        .filter(Review.user_id == user_id, Review.product_id == product_id)
        .first()
    )
    if existing:
        raise ConflictError("You have already reviewed this product")

    # Verify purchase: user must have a PAID order containing this product
    purchased = (
        db.query(OrderItem)
        .join(Order, Order.id == OrderItem.order_id)
        .filter(
            Order.user_id == user_id,
            Order.status == OrderStatus.PAID,
            OrderItem.product_id == product_id,
        )
        .first()
    )
    if purchased is None:
        raise AppException(
            status_code=403,
            detail="You can only review products you have purchased",
        )

    review = Review(user_id=user_id, product_id=product_id, **data)
    db.add(review)
    db.commit()
    db.refresh(review)
    logger.info(
        "review.created review_id=%s user_id=%s product_id=%s rating=%d",
        review.id, user_id, product_id, review.rating,
    )
    return _format_review(review)


def update_review(db: Session, user_id: str, review_id: str, data: dict) -> dict:
    review = db.query(Review).filter(Review.id == review_id).first()
    if review is None:
        raise NotFoundError("Review not found")
    if review.user_id != user_id:
        raise ForbiddenError()

    for key, value in data.items():
        setattr(review, key, value)
    db.commit()
    db.refresh(review)
    logger.info("review.updated review_id=%s user_id=%s", review.id, user_id)
    return _format_review(review)


def delete_review(db: Session, user_id: str, review_id: str) -> None:
    review = db.query(Review).filter(Review.id == review_id).first()
    if review is None:
        raise NotFoundError("Review not found")
    if review.user_id != user_id:
        raise ForbiddenError()

    db.delete(review)
    db.commit()
    logger.info("review.deleted review_id=%s user_id=%s", review_id, user_id)


def get_product_reviews(
    db: Session, product_id: str, include_hidden: bool = False
) -> list[dict]:
    query = db.query(Review).filter(Review.product_id == product_id)
    if not include_hidden:
        query = query.filter(Review.is_visible.is_(True))
    reviews = query.order_by(Review.created_at.desc()).all()
    return [_format_review(r) for r in reviews]


def admin_set_visibility(
    db: Session, review_id: str, visible: bool, admin_user_id: str | None = None
) -> dict:
    review = db.query(Review).filter(Review.id == review_id).first()
    if review is None:
        raise NotFoundError("Review not found")
    review.is_visible = visible

    action = "review.unhidden" if visible else "review.hidden"
    if admin_user_id:
        create_audit_log(
            db, admin_user_id, action,
            entity_type="review", entity_id=review.id,
            metadata={"rating": review.rating, "product_id": review.product_id},
        )

    # Notify user when their review is hidden
    if not visible:
        create_notification(
            db, review.user_id, "review_hidden",
            title="Review hidden",
            message=f"Your review for product has been hidden by a moderator.",
        )

    db.commit()
    db.refresh(review)
    logger.info("review.%s review_id=%s", "unhidden" if visible else "hidden", review.id)
    return _format_review(review)


def get_product_rating_stats(db: Session, product_id: str) -> dict:
    """Compute average_rating and reviews_count for a product (visible reviews only)."""
    result = (
        db.query(
            func.avg(Review.rating),
            func.count(Review.id),
        )
        .filter(Review.product_id == product_id, Review.is_visible.is_(True))
        .first()
    )
    avg_rating = round(float(result[0]), 2) if result[0] is not None else None
    count = result[1] or 0
    return {"average_rating": avg_rating, "reviews_count": count}


def get_products_rating_stats(db: Session, product_ids: list[str]) -> dict[str, dict]:
    """Bulk-fetch rating stats for multiple products."""
    if not product_ids:
        return {}
    rows = (
        db.query(
            Review.product_id,
            func.avg(Review.rating),
            func.count(Review.id),
        )
        .filter(Review.product_id.in_(product_ids), Review.is_visible.is_(True))
        .group_by(Review.product_id)
        .all()
    )
    stats = {}
    for pid, avg_r, cnt in rows:
        stats[pid] = {
            "average_rating": round(float(avg_r), 2) if avg_r is not None else None,
            "reviews_count": cnt,
        }
    return stats


def _format_review(review: Review) -> dict:
    return {
        "id": review.id,
        "user_id": review.user_id,
        "user_name": review.user.full_name,
        "product_id": review.product_id,
        "rating": review.rating,
        "title": review.title,
        "comment": review.comment,
        "is_visible": review.is_visible,
        "created_at": review.created_at,
        "updated_at": review.updated_at,
    }
