from sqlalchemy.orm import Session

from app.cart.models import Cart, CartItem
from app.catalog.models import Product
from app.exceptions import NotFoundError
from app.promotions.service import validate_coupon


def get_or_create_cart(db: Session, user_id: str) -> Cart:
    """Return the user's active (non-checked-out) cart, creating one if needed."""
    cart = (
        db.query(Cart)
        .filter(Cart.user_id == user_id, Cart.checked_out.is_(False))
        .first()
    )
    if cart is None:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


def get_cart(db: Session, user_id: str) -> dict:
    cart = get_or_create_cart(db, user_id)
    return _format_cart(cart)


def add_item(db: Session, user_id: str, product_id: str, quantity: int) -> dict:
    product = db.query(Product).filter(Product.id == product_id, Product.is_active.is_(True)).first()
    if product is None:
        raise NotFoundError("Product not found or is inactive")

    cart = get_or_create_cart(db, user_id)

    existing = (
        db.query(CartItem)
        .filter(CartItem.cart_id == cart.id, CartItem.product_id == product_id)
        .first()
    )

    if existing:
        existing.quantity += quantity
    else:
        item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
        db.add(item)

    db.commit()
    db.refresh(cart)
    return _format_cart(cart)


def update_item(db: Session, user_id: str, item_id: str, quantity: int) -> dict:
    cart = get_or_create_cart(db, user_id)
    item = (
        db.query(CartItem)
        .filter(CartItem.id == item_id, CartItem.cart_id == cart.id)
        .first()
    )
    if item is None:
        raise NotFoundError("Cart item not found")

    item.quantity = quantity
    db.commit()
    db.refresh(cart)
    return _format_cart(cart)


def remove_item(db: Session, user_id: str, item_id: str) -> dict:
    cart = get_or_create_cart(db, user_id)
    item = (
        db.query(CartItem)
        .filter(CartItem.id == item_id, CartItem.cart_id == cart.id)
        .first()
    )
    if item is None:
        raise NotFoundError("Cart item not found")

    db.delete(item)
    db.commit()
    db.refresh(cart)
    return _format_cart(cart)


def clear_cart(db: Session, user_id: str) -> dict:
    cart = get_or_create_cart(db, user_id)
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    db.commit()
    db.refresh(cart)
    return _format_cart(cart)


def apply_coupon(db: Session, user_id: str, code: str) -> dict:
    """Validate and attach a coupon to the cart. Replaces any existing coupon."""
    cart = get_or_create_cart(db, user_id)
    # Basic validation (no subtotal check — that happens at checkout)
    coupon = validate_coupon(db, code, user_id, subtotal=None)
    cart.coupon_code = coupon.code  # store normalized (uppercase) code
    db.commit()
    db.refresh(cart)
    return _format_cart(cart)


def remove_coupon(db: Session, user_id: str) -> dict:
    cart = get_or_create_cart(db, user_id)
    cart.coupon_code = None
    db.commit()
    db.refresh(cart)
    return _format_cart(cart)


def _format_cart(cart: Cart) -> dict:
    items = []
    total = 0.0

    for ci in cart.items:
        price = float(ci.product.price)
        subtotal = price * ci.quantity
        total += subtotal

        primary_image = None
        for img in ci.product.images:
            if img.is_primary:
                primary_image = img.url
                break
        if primary_image is None and ci.product.images:
            primary_image = ci.product.images[0].url

        items.append({
            "id": ci.id,
            "product_id": ci.product_id,
            "product_name": ci.product.name,
            "product_price": price,
            "product_slug": ci.product.slug,
            "primary_image": primary_image,
            "quantity": ci.quantity,
            "subtotal": round(subtotal, 2),
            "created_at": ci.created_at,
        })

    return {
        "id": cart.id,
        "items": items,
        "item_count": len(items),
        "total": round(total, 2),
        "coupon_code": cart.coupon_code,
        "updated_at": cart.updated_at,
    }
