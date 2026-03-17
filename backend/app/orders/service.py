import logging
from datetime import datetime

from sqlalchemy.orm import Session

from app.cart.models import Cart, CartItem
from app.catalog.models import Product
from app.exceptions import AppException, ConflictError, NotFoundError
from app.orders.models import IdempotencyKey, Order, OrderItem, OrderStatus
from app.payments.provider import PaymentProvider
from app.audit.service import create_audit_log
from app.notifications.service import create_notification
from app.promotions.models import Coupon
from app.promotions.service import calculate_discount, record_usage, validate_coupon

logger = logging.getLogger(__name__)


class InsufficientStockError(AppException):
    def __init__(self, product_name: str, available: int, requested: int):
        super().__init__(
            status_code=409,
            detail=(
                f"Insufficient stock for '{product_name}': "
                f"{available} available, {requested} requested"
            ),
        )


def checkout(
    db: Session,
    user_id: str,
    payment_provider: PaymentProvider,
    idempotency_key: str | None = None,
) -> dict:
    """
    Atomic checkout: cart → order.

    Transaction flow:
    0. If idempotency key provided, check for existing completed checkout
    1. Lock the user's active cart row (prevents double checkout from concurrent requests)
    2. Validate cart has items
    3. Lock each product row FOR UPDATE (prevents concurrent stock modification)
    4. Validate stock for every item
    5. Create Order + OrderItems with snapshotted prices
    6. Decrement product stock
    7. Process payment
    8. If payment succeeds → order=paid, cart=checked_out, COMMIT
    9. If payment fails → order=failed, restore stock, COMMIT
       (order saved as historical record; cart stays active so user can retry)
    10. If unexpected error → ROLLBACK (no partial state)
    """

    logger.info("checkout.start user_id=%s idempotency_key=%s", user_id, idempotency_key)

    # Step 0: Idempotency check — return existing order if already processed.
    # This covers both successful AND failed payments. A failed payment is a
    # completed operation; replaying the same key returns the same failed result.
    # To retry after failure, the client must use a new idempotency key.
    if idempotency_key:
        existing = (
            db.query(IdempotencyKey)
            .filter(
                IdempotencyKey.key == idempotency_key,
                IdempotencyKey.user_id == user_id,
            )
            .first()
        )
        if existing and existing.order_id:
            order = db.query(Order).filter(Order.id == existing.order_id).first()
            if order:
                logger.info(
                    "checkout.idempotent_hit user_id=%s key=%s order_id=%s status=%s",
                    user_id, idempotency_key, order.id, order.status.value,
                )
                return _format_checkout_response(order, "Order already processed (idempotent)")

    # Step 1: Lock the user's active cart to prevent double checkout.
    # Two concurrent requests: the second blocks here until the first commits.
    # After commit, if checked_out=True, this returns None → ConflictError.
    cart = (
        db.query(Cart)
        .filter(Cart.user_id == user_id, Cart.checked_out.is_(False))
        .with_for_update()
        .first()
    )

    # Step 2: Validate cart exists and has items.
    # No active cart (never created, or previous one was checked out) and
    # empty cart are both "nothing to checkout" — same error for the caller.
    if cart is None or not cart.items:
        raise AppException(status_code=400, detail="Cart is empty")

    cart_items: list[CartItem] = cart.items

    # Step 3: Lock product rows in a deterministic order to prevent deadlocks.
    # Sorting by product_id ensures all concurrent transactions lock rows
    # in the same order, which is the standard deadlock prevention technique.
    product_ids = sorted(set(ci.product_id for ci in cart_items))
    products: dict[str, Product] = {}
    for pid in product_ids:
        product = (
            db.query(Product)
            .filter(Product.id == pid)
            .with_for_update()
            .first()
        )
        if product is None:
            raise NotFoundError(f"Product '{pid}' no longer exists")
        if not product.is_active:
            raise AppException(
                status_code=409,
                detail=f"Product '{product.name}' is no longer available",
            )
        products[pid] = product

    # Step 4: Validate stock for every item
    for ci in cart_items:
        product = products[ci.product_id]
        if product.stock < ci.quantity:
            logger.warning(
                "checkout.insufficient_stock user_id=%s product=%s available=%d requested=%d",
                user_id, product.name, product.stock, ci.quantity,
            )
            raise InsufficientStockError(
                product_name=product.name,
                available=product.stock,
                requested=ci.quantity,
            )

    # Step 5: Calculate subtotal from cart items
    subtotal = 0.0
    item_data = []
    for ci in cart_items:
        product = products[ci.product_id]
        unit_price = float(product.price)
        line_total = round(unit_price * ci.quantity, 2)
        subtotal += line_total
        item_data.append((ci, unit_price))

    subtotal = round(subtotal, 2)

    # Step 5b: Validate and apply coupon if attached to cart
    coupon_code = cart.coupon_code
    coupon: Coupon | None = None
    discount_amount = 0.0
    if coupon_code:
        coupon = validate_coupon(db, coupon_code, user_id, subtotal)
        discount_amount = calculate_discount(coupon, subtotal)

    total = round(subtotal - discount_amount, 2)

    # Step 5c: Create order and items with snapshotted prices
    order = Order(
        user_id=user_id,
        cart_id=cart.id,
        status=OrderStatus.PENDING,
        subtotal=subtotal,
        discount_amount=discount_amount,
        total=total,
        coupon_code=coupon_code,
    )
    db.add(order)
    db.flush()  # Get order.id without committing

    for ci, unit_price in item_data:
        order_item = OrderItem(
            order_id=order.id,
            product_id=ci.product_id,
            quantity=ci.quantity,
            unit_price=unit_price,
        )
        db.add(order_item)

    # Step 6: Decrement stock
    for ci in cart_items:
        products[ci.product_id].stock -= ci.quantity

    db.flush()

    # Step 7: Process payment
    payment_result = payment_provider.process_payment(amount=order.total)

    # Step 8/9: Handle result
    if payment_result.success:
        order.status = OrderStatus.PAID
        cart.checked_out = True
        # Record coupon usage inside the same transaction
        if coupon is not None:
            record_usage(db, coupon, user_id, order.id)
        create_notification(
            db, user_id, "order_paid",
            title="Order confirmed",
            message=f"Your order #{order.id[:8]} has been paid. Total: ${order.total:.2f}",
        )
        logger.info(
            "checkout.success order_id=%s user_id=%s total=%.2f discount=%.2f",
            order.id, user_id, order.total, discount_amount,
        )
    else:
        order.status = OrderStatus.FAILED
        # Restore stock — order exists as a failed record, cart stays active
        for ci in cart_items:
            products[ci.product_id].stock += ci.quantity
        create_notification(
            db, user_id, "order_failed",
            title="Payment failed",
            message=f"Payment for order #{order.id[:8]} failed: {payment_result.message}",
        )
        logger.warning(
            "checkout.payment_failed order_id=%s user_id=%s message=%s",
            order.id, user_id, payment_result.message,
        )

    # Store idempotency key → order mapping
    if idempotency_key:
        idem = IdempotencyKey(
            key=idempotency_key, user_id=user_id, order_id=order.id
        )
        db.add(idem)

    db.commit()
    db.refresh(order)

    return _format_checkout_response(order, payment_result.message)


def get_user_orders(db: Session, user_id: str) -> list[dict]:
    orders = (
        db.query(Order)
        .filter(Order.user_id == user_id)
        .order_by(Order.created_at.desc())
        .all()
    )
    return [_format_order(o) for o in orders]


def get_all_orders(
    db: Session,
    status: str | None = None,
    user_id: str | None = None,
    created_after: datetime | None = None,
    created_before: datetime | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict:
    query = db.query(Order)
    if status:
        query = query.filter(Order.status == status)
    if user_id:
        query = query.filter(Order.user_id == user_id)
    if created_after:
        query = query.filter(Order.created_at >= created_after)
    if created_before:
        query = query.filter(Order.created_at <= created_before)

    total = query.count()
    items = query.order_by(Order.created_at.desc()).offset(offset).limit(limit).all()

    return {
        "items": [_format_order(o) for o in items],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


def admin_get_order(db: Session, order_id: str) -> dict:
    order = db.query(Order).filter(Order.id == order_id).first()
    if order is None:
        raise NotFoundError("Order not found")
    return _format_order(order)


def cancel_order(db: Session, order_id: str, admin_user_id: str | None = None) -> dict:
    # Lock the order row to prevent concurrent cancellation from restoring
    # stock twice. Same defensive pattern as checkout's cart locking.
    order = (
        db.query(Order)
        .filter(Order.id == order_id)
        .with_for_update()
        .first()
    )
    if order is None:
        raise NotFoundError("Order not found")
    if order.status != OrderStatus.PAID:
        raise AppException(
            status_code=409,
            detail=f"Only paid orders can be cancelled (current status: {order.status.value})",
        )

    # Lock product rows in sorted order to prevent deadlocks (same as checkout)
    product_ids = sorted(set(oi.product_id for oi in order.items))
    products: dict[str, Product] = {}
    for pid in product_ids:
        product = (
            db.query(Product)
            .filter(Product.id == pid)
            .with_for_update()
            .first()
        )
        if product is not None:
            products[pid] = product

    # Restore stock for each order item
    for oi in order.items:
        if oi.product_id in products:
            products[oi.product_id].stock += oi.quantity

    order.status = OrderStatus.CANCELLED

    create_notification(
        db, order.user_id, "order_cancelled",
        title="Order cancelled",
        message=f"Your order #{order.id[:8]} has been cancelled by an administrator.",
    )
    if admin_user_id:
        create_audit_log(
            db, admin_user_id, "order.cancelled",
            entity_type="order", entity_id=order.id,
            metadata={"total": float(order.total), "items": len(order.items)},
        )

    db.commit()
    db.refresh(order)

    logger.info("order.cancelled order_id=%s items=%d", order.id, len(order.items))
    return _format_order(order)


def get_order_by_id(db: Session, user_id: str, order_id: str) -> dict:
    order = (
        db.query(Order)
        .filter(Order.id == order_id, Order.user_id == user_id)
        .first()
    )
    if order is None:
        raise NotFoundError("Order not found")
    return _format_order(order)


def _format_order(order: Order) -> dict:
    return {
        "id": order.id,
        "status": order.status,
        "subtotal": float(order.subtotal),
        "discount_amount": float(order.discount_amount),
        "total": float(order.total),
        "coupon_code": order.coupon_code,
        "items": [
            {
                "id": oi.id,
                "product_id": oi.product_id,
                "product_name": oi.product.name,
                "quantity": oi.quantity,
                "unit_price": float(oi.unit_price),
                "subtotal": round(float(oi.unit_price) * oi.quantity, 2),
            }
            for oi in order.items
        ],
        "created_at": order.created_at,
        "updated_at": order.updated_at,
    }


def _format_checkout_response(order: Order, payment_message: str) -> dict:
    return {
        "order": _format_order(order),
        "payment_message": payment_message,
    }
