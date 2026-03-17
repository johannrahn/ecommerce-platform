from datetime import datetime

from pydantic import BaseModel

from app.orders.models import OrderStatus


class OrderItemResponse(BaseModel):
    id: str
    product_id: str
    product_name: str
    quantity: int
    unit_price: float
    subtotal: float

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    id: str
    status: OrderStatus
    subtotal: float
    discount_amount: float
    total: float
    coupon_code: str | None
    items: list[OrderItemResponse]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaginatedOrders(BaseModel):
    items: list[OrderResponse]
    total: int
    limit: int
    offset: int


class CheckoutResponse(BaseModel):
    order: OrderResponse
    payment_message: str
