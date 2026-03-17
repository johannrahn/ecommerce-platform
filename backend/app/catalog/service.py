import logging
import math

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.audit.service import create_audit_log
from app.catalog.models import Category, Product, ProductImage
from app.exceptions import ConflictError, NotFoundError

logger = logging.getLogger(__name__)


# --------------- Categories ---------------

def get_categories(db: Session, include_inactive: bool = False) -> list[Category]:
    query = db.query(Category)
    if not include_inactive:
        query = query.filter(Category.is_active.is_(True))
    return query.order_by(Category.name).all()


def get_category_by_id(db: Session, category_id: str) -> Category:
    category = db.query(Category).filter(Category.id == category_id).first()
    if category is None:
        raise NotFoundError("Category not found")
    return category


def get_category_by_slug(db: Session, slug: str) -> Category:
    category = db.query(Category).filter(Category.slug == slug).first()
    if category is None:
        raise NotFoundError("Category not found")
    return category


def create_category(db: Session, data: dict) -> Category:
    if db.query(Category).filter(Category.slug == data["slug"]).first():
        raise ConflictError("A category with this slug already exists")
    if db.query(Category).filter(Category.name == data["name"]).first():
        raise ConflictError("A category with this name already exists")

    category = Category(**data)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_category(db: Session, category_id: str, data: dict) -> Category:
    category = get_category_by_id(db, category_id)

    if "slug" in data and data["slug"] != category.slug:
        existing = db.query(Category).filter(Category.slug == data["slug"]).first()
        if existing:
            raise ConflictError("A category with this slug already exists")

    if "name" in data and data["name"] != category.name:
        existing = db.query(Category).filter(Category.name == data["name"]).first()
        if existing:
            raise ConflictError("A category with this name already exists")

    for key, value in data.items():
        setattr(category, key, value)
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category_id: str) -> None:
    category = get_category_by_id(db, category_id)
    product_count = db.query(Product).filter(Product.category_id == category_id).count()
    if product_count > 0:
        raise ConflictError(
            f"Cannot delete category with {product_count} product(s). "
            "Reassign or delete them first."
        )
    db.delete(category)
    db.commit()


# --------------- Products ---------------

def get_products(
    db: Session,
    page: int = 1,
    per_page: int = 20,
    category_id: str | None = None,
    search: str | None = None,
    include_inactive: bool = False,
) -> dict:
    query = db.query(Product).options(
        joinedload(Product.category),
        joinedload(Product.images),
    )

    if not include_inactive:
        query = query.filter(Product.is_active.is_(True))

    if category_id:
        query = query.filter(Product.category_id == category_id)

    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    total = query.count()
    pages = math.ceil(total / per_page) if total > 0 else 1
    items = query.order_by(Product.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": pages,
    }


def get_product_by_id(db: Session, product_id: str) -> Product:
    product = (
        db.query(Product)
        .options(joinedload(Product.category), joinedload(Product.images))
        .filter(Product.id == product_id)
        .first()
    )
    if product is None:
        raise NotFoundError("Product not found")
    return product


def get_product_by_slug(db: Session, slug: str) -> Product:
    product = (
        db.query(Product)
        .options(joinedload(Product.category), joinedload(Product.images))
        .filter(Product.slug == slug)
        .first()
    )
    if product is None:
        raise NotFoundError("Product not found")
    return product


def create_product(db: Session, data: dict) -> Product:
    if db.query(Product).filter(Product.slug == data["slug"]).first():
        raise ConflictError("A product with this slug already exists")

    get_category_by_id(db, data["category_id"])

    images_data = data.pop("images", [])
    product = Product(**data)
    db.add(product)
    db.flush()

    for img in images_data:
        image = ProductImage(product_id=product.id, **img)
        db.add(image)

    db.commit()
    db.refresh(product)
    return get_product_by_id(db, product.id)


def update_product(
    db: Session, product_id: str, data: dict, admin_user_id: str | None = None
) -> Product:
    product = get_product_by_id(db, product_id)

    if "slug" in data and data["slug"] != product.slug:
        existing = db.query(Product).filter(Product.slug == data["slug"]).first()
        if existing:
            raise ConflictError("A product with this slug already exists")

    if "category_id" in data:
        get_category_by_id(db, data["category_id"])

    old_stock = product.stock
    old_active = product.is_active

    for key, value in data.items():
        setattr(product, key, value)

    if admin_user_id:
        if "stock" in data and data["stock"] != old_stock:
            create_audit_log(
                db, admin_user_id, "product.stock_updated",
                entity_type="product", entity_id=product_id,
                metadata={"old_stock": old_stock, "new_stock": data["stock"]},
            )
        if "is_active" in data and data["is_active"] != old_active:
            create_audit_log(
                db, admin_user_id, "product.active_changed",
                entity_type="product", entity_id=product_id,
                metadata={"is_active": data["is_active"]},
            )

    db.commit()
    db.refresh(product)

    if "stock" in data and data["stock"] != old_stock:
        logger.info(
            "product.stock_updated product_id=%s old=%d new=%d",
            product_id, old_stock, data["stock"],
        )
    if "is_active" in data and data["is_active"] != old_active:
        logger.info(
            "product.active_changed product_id=%s is_active=%s",
            product_id, data["is_active"],
        )

    return get_product_by_id(db, product.id)


def delete_product(db: Session, product_id: str) -> None:
    product = get_product_by_id(db, product_id)
    db.delete(product)
    db.commit()


# --------------- Product Images ---------------

def add_product_image(db: Session, product_id: str, data: dict) -> Product:
    get_product_by_id(db, product_id)
    image = ProductImage(product_id=product_id, **data)
    db.add(image)
    db.commit()
    return get_product_by_id(db, product_id)


def delete_product_image(db: Session, image_id: str) -> None:
    image = db.query(ProductImage).filter(ProductImage.id == image_id).first()
    if image is None:
        raise NotFoundError("Image not found")
    db.delete(image)
    db.commit()
