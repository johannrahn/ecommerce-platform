from datetime import datetime

from pydantic import BaseModel, Field

from app.promotions.models import DiscountType


class CouponCreate(BaseModel):
    code: str = Field(max_length=50)
    description: str | None = Field(default=None, max_length=500)
    discount_type: DiscountType
    discount_value: float = Field(gt=0)
    minimum_order_amount: float | None = Field(default=None, ge=0)
    max_discount_amount: float | None = Field(default=None, gt=0)
    max_uses: int | None = Field(default=None, ge=1)
    is_active: bool = True
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    one_per_user: bool = False


class CouponUpdate(BaseModel):
    code: str | None = Field(default=None, max_length=50)
    description: str | None = Field(default=None, max_length=500)
    discount_type: DiscountType | None = None
    discount_value: float | None = Field(default=None, gt=0)
    minimum_order_amount: float | None = None
    max_discount_amount: float | None = None
    max_uses: int | None = Field(default=None, ge=1)
    is_active: bool | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    one_per_user: bool | None = None


class CouponResponse(BaseModel):
    id: str
    code: str
    description: str | None
    discount_type: DiscountType
    discount_value: float
    minimum_order_amount: float | None
    max_discount_amount: float | None
    max_uses: int | None
    used_count: int
    is_active: bool
    starts_at: datetime | None
    ends_at: datetime | None
    one_per_user: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
