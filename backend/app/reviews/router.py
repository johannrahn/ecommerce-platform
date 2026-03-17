from typing import Annotated

from fastapi import APIRouter, Depends

from app.catalog import service as catalog_service
from app.dependencies import DBSession, get_current_user, require_admin
from app.reviews import service
from app.reviews.schemas import ReviewCreate, ReviewResponse, ReviewUpdate
from app.users.models import User

CurrentUser = Annotated[User, Depends(get_current_user)]
AdminUser = Annotated[User, Depends(require_admin)]

# ============================================================
# Public / authenticated routes
# ============================================================

router = APIRouter(tags=["reviews"])


@router.post(
    "/products/{slug}/reviews",
    response_model=ReviewResponse,
    status_code=201,
    summary="Create a product review",
)
def create_review(slug: str, data: ReviewCreate, current_user: CurrentUser, db: DBSession):
    product = catalog_service.get_product_by_slug(db, slug)
    return service.create_review(db, current_user.id, product.id, data.model_dump())


@router.get(
    "/products/{slug}/reviews",
    response_model=list[ReviewResponse],
    summary="List product reviews",
)
def list_product_reviews(slug: str, db: DBSession):
    product = catalog_service.get_product_by_slug(db, slug)
    return service.get_product_reviews(db, product.id)


@router.put(
    "/reviews/{review_id}",
    response_model=ReviewResponse,
    summary="Update my review",
)
def update_review(
    review_id: str, data: ReviewUpdate, current_user: CurrentUser, db: DBSession
):
    return service.update_review(
        db, current_user.id, review_id, data.model_dump(exclude_unset=True)
    )


@router.delete(
    "/reviews/{review_id}",
    status_code=204,
    summary="Delete my review",
)
def delete_review(review_id: str, current_user: CurrentUser, db: DBSession):
    service.delete_review(db, current_user.id, review_id)


# ============================================================
# Admin moderation
# ============================================================

admin_router = APIRouter(prefix="/admin/reviews", tags=["admin-reviews"])


@admin_router.post(
    "/{review_id}/hide",
    response_model=ReviewResponse,
    summary="Hide a review",
)
def admin_hide_review(review_id: str, admin: AdminUser, db: DBSession):
    return service.admin_set_visibility(db, review_id, visible=False, admin_user_id=admin.id)


@admin_router.post(
    "/{review_id}/unhide",
    response_model=ReviewResponse,
    summary="Unhide a review",
)
def admin_unhide_review(review_id: str, admin: AdminUser, db: DBSession):
    return service.admin_set_visibility(db, review_id, visible=True, admin_user_id=admin.id)
