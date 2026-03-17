from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies import DBSession, require_admin
from app.promotions import service
from app.promotions.schemas import CouponCreate, CouponResponse, CouponUpdate
from app.users.models import User

AdminUser = Annotated[User, Depends(require_admin)]

admin_router = APIRouter(prefix="/admin/coupons", tags=["admin-coupons"])


@admin_router.post(
    "",
    response_model=CouponResponse,
    status_code=201,
    summary="Create coupon",
)
def admin_create_coupon(data: CouponCreate, admin: AdminUser, db: DBSession):
    return service.create_coupon(db, data.model_dump(), admin_user_id=admin.id)


@admin_router.get(
    "",
    response_model=list[CouponResponse],
    summary="List coupons",
)
def admin_list_coupons(admin: AdminUser, db: DBSession):
    return service.list_coupons(db, include_inactive=True)


@admin_router.get(
    "/{coupon_id}",
    response_model=CouponResponse,
    summary="Get coupon detail",
)
def admin_get_coupon(coupon_id: str, admin: AdminUser, db: DBSession):
    return service.get_coupon(db, coupon_id)


@admin_router.put(
    "/{coupon_id}",
    response_model=CouponResponse,
    summary="Update coupon",
)
def admin_update_coupon(
    coupon_id: str, data: CouponUpdate, admin: AdminUser, db: DBSession
):
    return service.update_coupon(db, coupon_id, data.model_dump(exclude_unset=True), admin_user_id=admin.id)
