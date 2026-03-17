from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Header, Query

from app.dependencies import DBSession, get_current_user, require_admin
from app.orders import service
from app.orders.models import OrderStatus
from app.orders.schemas import CheckoutResponse, OrderResponse, PaginatedOrders
from app.payments.provider import PaymentProvider, get_payment_provider
from app.users.models import User

router = APIRouter(prefix="/orders", tags=["orders"])

CurrentUser = Annotated[User, Depends(get_current_user)]
AdminUser = Annotated[User, Depends(require_admin)]


@router.post("/checkout", response_model=CheckoutResponse, summary="Checkout cart")
def checkout(
    current_user: CurrentUser,
    db: DBSession,
    payment_provider: Annotated[PaymentProvider, Depends(get_payment_provider)],
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
):
    return service.checkout(
        db,
        current_user.id,
        payment_provider,
        idempotency_key=idempotency_key,
    )


@router.get("", response_model=list[OrderResponse], summary="List my orders")
def list_my_orders(current_user: CurrentUser, db: DBSession):
    return service.get_user_orders(db, current_user.id)


@router.get("/{order_id}", response_model=OrderResponse, summary="Get my order")
def get_order(order_id: str, current_user: CurrentUser, db: DBSession):
    return service.get_order_by_id(db, current_user.id, order_id)


# ============================================================
# Admin routes
# ============================================================

admin_router = APIRouter(prefix="/admin/orders", tags=["admin-orders"])


@admin_router.get("", response_model=PaginatedOrders, summary="List all orders")
def admin_list_orders(
    admin: AdminUser,
    db: DBSession,
    status: OrderStatus | None = Query(default=None, description="Filter by order status"),
    user_id: str | None = Query(default=None, description="Filter by user ID"),
    created_after: datetime | None = Query(default=None, description="Orders created after"),
    created_before: datetime | None = Query(default=None, description="Orders created before"),
    limit: int = Query(default=20, ge=1, le=100, description="Max items per page"),
    offset: int = Query(default=0, ge=0, description="Items to skip"),
):
    return service.get_all_orders(
        db,
        status=status.value if status else None,
        user_id=user_id,
        created_after=created_after,
        created_before=created_before,
        limit=limit,
        offset=offset,
    )


@admin_router.get("/{order_id}", response_model=OrderResponse, summary="Get order details")
def admin_get_order(order_id: str, admin: AdminUser, db: DBSession):
    return service.admin_get_order(db, order_id)


@admin_router.post(
    "/{order_id}/cancel", response_model=OrderResponse, summary="Cancel a paid order"
)
def admin_cancel_order(order_id: str, admin: AdminUser, db: DBSession):
    return service.cancel_order(db, order_id, admin_user_id=admin.id)
