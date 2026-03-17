from typing import Annotated

from fastapi import APIRouter, Depends

from app.cart import service
from app.cart.schemas import ApplyCoupon, CartItemAdd, CartItemUpdate, CartResponse
from app.dependencies import DBSession, get_current_user
from app.users.models import User

router = APIRouter(prefix="/cart", tags=["cart"])

CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get("", response_model=CartResponse, summary="Get my cart")
def get_cart(current_user: CurrentUser, db: DBSession):
    return service.get_cart(db, current_user.id)


@router.post("/items", response_model=CartResponse, summary="Add item to cart")
def add_item(data: CartItemAdd, current_user: CurrentUser, db: DBSession):
    return service.add_item(db, current_user.id, data.product_id, data.quantity)


@router.put("/items/{item_id}", response_model=CartResponse, summary="Update item quantity")
def update_item(item_id: str, data: CartItemUpdate, current_user: CurrentUser, db: DBSession):
    return service.update_item(db, current_user.id, item_id, data.quantity)


@router.delete("/items/{item_id}", response_model=CartResponse, summary="Remove item from cart")
def remove_item(item_id: str, current_user: CurrentUser, db: DBSession):
    return service.remove_item(db, current_user.id, item_id)


@router.post("/coupon", response_model=CartResponse, summary="Apply coupon to cart")
def apply_coupon(data: ApplyCoupon, current_user: CurrentUser, db: DBSession):
    return service.apply_coupon(db, current_user.id, data.code)


@router.delete("/coupon", response_model=CartResponse, summary="Remove coupon from cart")
def remove_coupon(current_user: CurrentUser, db: DBSession):
    return service.remove_coupon(db, current_user.id)


@router.delete("", response_model=CartResponse, summary="Clear cart")
def clear_cart(current_user: CurrentUser, db: DBSession):
    return service.clear_cart(db, current_user.id)
