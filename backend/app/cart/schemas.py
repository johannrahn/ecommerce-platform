from datetime import datetime

from pydantic import BaseModel, Field


class CartItemAdd(BaseModel):
    product_id: str
    quantity: int = Field(ge=1)


class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=1)


class CartItemResponse(BaseModel):
    id: str
    product_id: str
    product_name: str
    product_price: float
    product_slug: str
    primary_image: str | None
    quantity: int
    subtotal: float
    created_at: datetime

    model_config = {"from_attributes": True}


class ApplyCoupon(BaseModel):
    code: str = Field(max_length=50)


class CartResponse(BaseModel):
    id: str
    items: list[CartItemResponse]
    item_count: int
    total: float
    coupon_code: str | None = None
    updated_at: datetime
