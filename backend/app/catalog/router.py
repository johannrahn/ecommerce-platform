from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.catalog import service
from app.catalog.schemas import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
    PaginatedProducts,
    ProductCreate,
    ProductImageCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
)
from app.dependencies import DBSession, get_current_user, require_admin
from app.reviews.service import get_product_rating_stats, get_products_rating_stats
from app.users.models import User

AdminUser = Annotated[User, Depends(require_admin)]

# ============================================================
# Public routes
# ============================================================

public_router = APIRouter(prefix="/catalog", tags=["catalog"])


@public_router.get("/categories", response_model=list[CategoryResponse], summary="List categories")
def list_categories(db: DBSession):
    return service.get_categories(db)


@public_router.get("/categories/{slug}", response_model=CategoryResponse, summary="Get category by slug")
def get_category(slug: str, db: DBSession):
    return service.get_category_by_slug(db, slug)


@public_router.get("/products", response_model=PaginatedProducts, summary="List products")
def list_products(
    db: DBSession,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category_id: str | None = None,
    search: str | None = None,
):
    result = service.get_products(
        db, page=page, per_page=per_page, category_id=category_id, search=search
    )
    return _format_paginated(db, result)


@public_router.get("/products/{slug}", response_model=ProductResponse, summary="Get product by slug")
def get_product(slug: str, db: DBSession):
    return _format_product_detail(db, service.get_product_by_slug(db, slug))


# ============================================================
# Admin routes
# ============================================================

admin_router = APIRouter(prefix="/admin/catalog", tags=["admin-catalog"])


# --- Categories ---

@admin_router.get("/categories", response_model=list[CategoryResponse], summary="List all categories")
def admin_list_categories(admin: AdminUser, db: DBSession):
    return service.get_categories(db, include_inactive=True)


@admin_router.post("/categories", response_model=CategoryResponse, status_code=201, summary="Create category")
def admin_create_category(data: CategoryCreate, admin: AdminUser, db: DBSession):
    return service.create_category(db, data.model_dump())


@admin_router.put("/categories/{category_id}", response_model=CategoryResponse, summary="Update category")
def admin_update_category(
    category_id: str, data: CategoryUpdate, admin: AdminUser, db: DBSession
):
    return service.update_category(db, category_id, data.model_dump(exclude_unset=True))


@admin_router.delete("/categories/{category_id}", status_code=204, summary="Delete category")
def admin_delete_category(category_id: str, admin: AdminUser, db: DBSession):
    service.delete_category(db, category_id)


# --- Products ---

@admin_router.get("/products", response_model=PaginatedProducts, summary="List all products")
def admin_list_products(
    admin: AdminUser,
    db: DBSession,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category_id: str | None = None,
    search: str | None = None,
):
    result = service.get_products(
        db, page=page, per_page=per_page, category_id=category_id,
        search=search, include_inactive=True,
    )
    return _format_paginated(db, result)


@admin_router.post("/products", response_model=ProductResponse, status_code=201, summary="Create product")
def admin_create_product(data: ProductCreate, admin: AdminUser, db: DBSession):
    return _format_product_detail(db, service.create_product(db, data.model_dump()))


@admin_router.get("/products/{product_id}", response_model=ProductResponse, summary="Get product by ID")
def admin_get_product(product_id: str, admin: AdminUser, db: DBSession):
    return _format_product_detail(db, service.get_product_by_id(db, product_id))


@admin_router.put("/products/{product_id}", response_model=ProductResponse, summary="Update product")
def admin_update_product(
    product_id: str, data: ProductUpdate, admin: AdminUser, db: DBSession
):
    return _format_product_detail(
        db, service.update_product(db, product_id, data.model_dump(exclude_unset=True), admin_user_id=admin.id)
    )


@admin_router.delete("/products/{product_id}", status_code=204, summary="Delete product")
def admin_delete_product(product_id: str, admin: AdminUser, db: DBSession):
    service.delete_product(db, product_id)


# --- Product Images ---

@admin_router.post(
    "/products/{product_id}/images", response_model=ProductResponse, status_code=201,
    summary="Add product image",
)
def admin_add_product_image(
    product_id: str, data: ProductImageCreate, admin: AdminUser, db: DBSession
):
    return _format_product_detail(db, service.add_product_image(db, product_id, data.model_dump()))


@admin_router.delete("/images/{image_id}", status_code=204, summary="Delete product image")
def admin_delete_product_image(image_id: str, admin: AdminUser, db: DBSession):
    service.delete_product_image(db, image_id)


# ============================================================
# Helpers
# ============================================================

def _format_paginated(db, result: dict) -> dict:
    """Convert raw product list to ProductListResponse format with rating stats."""
    product_ids = [p.id for p in result["items"]]
    stats = get_products_rating_stats(db, product_ids)

    items = []
    for p in result["items"]:
        primary = next((img.url for img in p.images if img.is_primary), None)
        if primary is None and p.images:
            primary = p.images[0].url
        p_stats = stats.get(p.id, {"average_rating": None, "reviews_count": 0})
        items.append({
            "id": p.id,
            "name": p.name,
            "slug": p.slug,
            "price": float(p.price),
            "stock": p.stock,
            "category": p.category,
            "primary_image": primary,
            "is_active": p.is_active,
            "average_rating": p_stats["average_rating"],
            "reviews_count": p_stats["reviews_count"],
        })
    return {
        "items": items,
        "total": result["total"],
        "page": result["page"],
        "per_page": result["per_page"],
        "pages": result["pages"],
    }


def _format_product_detail(db, product) -> dict:
    """Convert ORM Product to dict with rating stats."""
    stats = get_product_rating_stats(db, product.id)
    return {
        "id": product.id,
        "name": product.name,
        "slug": product.slug,
        "description": product.description,
        "price": float(product.price),
        "stock": product.stock,
        "category_id": product.category_id,
        "category": product.category,
        "images": product.images,
        "is_active": product.is_active,
        "average_rating": stats["average_rating"],
        "reviews_count": stats["reviews_count"],
        "created_at": product.created_at,
        "updated_at": product.updated_at,
    }
