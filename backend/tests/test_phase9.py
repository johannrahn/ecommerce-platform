import pytest
from datetime import datetime, timezone, timedelta

from app.auth.security import hash_password
from app.payments.provider import SimulatedProvider, get_payment_provider
from app.main import app
from app.users.models import User, UserRole


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture()
def admin_token(client, db):
    user = User(
        email="admin@test.com",
        hashed_password=hash_password("admin123"),
        full_name="Admin",
        role=UserRole.ADMIN,
    )
    db.add(user)
    db.commit()
    resp = client.post("/api/auth/login", json={"email": "admin@test.com", "password": "admin123"})
    return resp.json()["access_token"]


@pytest.fixture()
def customer_token(client):
    client.post(
        "/api/auth/register",
        json={"email": "cust@test.com", "password": "cust123", "full_name": "Customer"},
    )
    resp = client.post("/api/auth/login", json={"email": "cust@test.com", "password": "cust123"})
    return resp.json()["access_token"]


@pytest.fixture()
def customer2_token(client):
    client.post(
        "/api/auth/register",
        json={"email": "cust2@test.com", "password": "cust2123", "full_name": "Customer2"},
    )
    resp = client.post("/api/auth/login", json={"email": "cust2@test.com", "password": "cust2123"})
    return resp.json()["access_token"]


@pytest.fixture()
def category_id(client, admin_token):
    resp = client.post(
        "/api/admin/catalog/categories",
        headers=_auth(admin_token),
        json={"name": "Perfume", "slug": "perfume"},
    )
    return resp.json()["id"]


@pytest.fixture()
def product_a(client, admin_token, category_id):
    """Product with stock=10, price=100.00"""
    resp = client.post(
        "/api/admin/catalog/products",
        headers=_auth(admin_token),
        json={
            "name": "Midnight Oud",
            "slug": "midnight-oud",
            "price": 100.00,
            "stock": 10,
            "category_id": category_id,
        },
    )
    return resp.json()["id"]


@pytest.fixture()
def product_b(client, admin_token, category_id):
    """Product with stock=5, price=50.00"""
    resp = client.post(
        "/api/admin/catalog/products",
        headers=_auth(admin_token),
        json={
            "name": "Citrus Breeze",
            "slug": "citrus-breeze",
            "price": 50.00,
            "stock": 5,
            "category_id": category_id,
        },
    )
    return resp.json()["id"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _add_to_cart(client, token, product_id, quantity=1):
    return client.post(
        "/api/cart/items",
        headers=_auth(token),
        json={"product_id": product_id, "quantity": quantity},
    )


def _apply_coupon(client, token, code):
    return client.post(
        "/api/cart/coupon",
        headers=_auth(token),
        json={"code": code},
    )


def _remove_coupon(client, token):
    return client.delete("/api/cart/coupon", headers=_auth(token))


def _checkout(client, token):
    return client.post("/api/orders/checkout", headers=_auth(token))


def _create_coupon(client, admin_token, **overrides):
    data = {
        "code": "SAVE10",
        "discount_type": "percent",
        "discount_value": 10,
    }
    data.update(overrides)
    return client.post(
        "/api/admin/coupons",
        headers=_auth(admin_token),
        json=data,
    )


# ============================================================
# Cart Coupon Endpoints
# ============================================================

class TestCartCoupon:
    def test_apply_coupon_to_cart(self, client, admin_token, customer_token, product_a):
        _create_coupon(client, admin_token, code="CART10")
        _add_to_cart(client, customer_token, product_a, quantity=1)

        resp = _apply_coupon(client, customer_token, "CART10")
        assert resp.status_code == 200
        assert resp.json()["coupon_code"] == "CART10"

    def test_remove_coupon_from_cart(self, client, admin_token, customer_token, product_a):
        _create_coupon(client, admin_token, code="REMOVE")
        _add_to_cart(client, customer_token, product_a, quantity=1)
        _apply_coupon(client, customer_token, "REMOVE")

        resp = _remove_coupon(client, customer_token)
        assert resp.status_code == 200
        assert resp.json()["coupon_code"] is None

    def test_replace_existing_coupon(self, client, admin_token, customer_token, product_a):
        _create_coupon(client, admin_token, code="FIRST1")
        _create_coupon(client, admin_token, code="SECOND2")
        _add_to_cart(client, customer_token, product_a, quantity=1)

        _apply_coupon(client, customer_token, "FIRST1")
        resp = _apply_coupon(client, customer_token, "SECOND2")
        assert resp.status_code == 200
        assert resp.json()["coupon_code"] == "SECOND2"

    def test_cart_shows_coupon_in_get(self, client, admin_token, customer_token, product_a):
        _create_coupon(client, admin_token, code="VISIBLE")
        _add_to_cart(client, customer_token, product_a, quantity=1)
        _apply_coupon(client, customer_token, "VISIBLE")

        resp = client.get("/api/cart", headers=_auth(customer_token))
        assert resp.status_code == 200
        assert resp.json()["coupon_code"] == "VISIBLE"

    def test_apply_invalid_coupon(self, client, customer_token, product_a):
        _add_to_cart(client, customer_token, product_a, quantity=1)
        resp = _apply_coupon(client, customer_token, "NONEXISTENT")
        assert resp.status_code == 404

    def test_remove_coupon_when_none_applied(self, client, customer_token):
        resp = _remove_coupon(client, customer_token)
        assert resp.status_code == 200
        assert resp.json()["coupon_code"] is None

    def test_apply_coupon_unauthenticated(self, client):
        resp = client.post("/api/cart/coupon", json={"code": "ABC"})
        assert resp.status_code == 401


# ============================================================
# Case-insensitive Coupon Codes
# ============================================================

class TestCaseInsensitive:
    def test_apply_lowercase_code(self, client, admin_token, customer_token, product_a):
        _create_coupon(client, admin_token, code="UPPERCASE")
        _add_to_cart(client, customer_token, product_a, quantity=1)

        resp = _apply_coupon(client, customer_token, "uppercase")
        assert resp.status_code == 200
        assert resp.json()["coupon_code"] == "UPPERCASE"  # stored as uppercase

    def test_apply_mixed_case_code(self, client, admin_token, customer_token, product_a):
        _create_coupon(client, admin_token, code="MIXED")
        _add_to_cart(client, customer_token, product_a, quantity=1)

        resp = _apply_coupon(client, customer_token, "MiXeD")
        assert resp.status_code == 200
        assert resp.json()["coupon_code"] == "MIXED"

    def test_create_duplicate_case_insensitive(self, client, admin_token):
        _create_coupon(client, admin_token, code="UNIQUE")
        resp = _create_coupon(client, admin_token, code="unique")
        assert resp.status_code == 409

    def test_checkout_with_lowercase_applied_coupon(
        self, client, admin_token, customer_token, product_a
    ):
        _create_coupon(
            client, admin_token, code="DISC15",
            discount_type="fixed", discount_value=15,
        )
        _add_to_cart(client, customer_token, product_a, quantity=1)
        _apply_coupon(client, customer_token, "disc15")

        resp = _checkout(client, customer_token)
        assert resp.status_code == 200
        order = resp.json()["order"]
        assert order["discount_amount"] == 15.0
        assert order["coupon_code"] == "DISC15"


# ============================================================
# max_discount_amount (Cap for Percent Coupons)
# ============================================================

class TestMaxDiscountAmount:
    def test_percent_capped_by_max_discount(self, client, admin_token, customer_token, product_a):
        """20% of 200 = 40, but max_discount_amount=25 caps it."""
        _create_coupon(
            client, admin_token,
            code="CAP25", discount_type="percent", discount_value=20,
            max_discount_amount=25,
        )
        _add_to_cart(client, customer_token, product_a, quantity=2)  # subtotal=200
        _apply_coupon(client, customer_token, "CAP25")

        resp = _checkout(client, customer_token)
        assert resp.status_code == 200
        order = resp.json()["order"]
        assert order["subtotal"] == 200.0
        assert order["discount_amount"] == 25.0  # capped at max_discount_amount
        assert order["total"] == 175.0

    def test_percent_below_max_discount(self, client, admin_token, customer_token, product_b):
        """10% of 50 = 5, max_discount_amount=25 is NOT reached."""
        _create_coupon(
            client, admin_token,
            code="BELOW", discount_type="percent", discount_value=10,
            max_discount_amount=25,
        )
        _add_to_cart(client, customer_token, product_b, quantity=1)  # subtotal=50
        _apply_coupon(client, customer_token, "BELOW")

        resp = _checkout(client, customer_token)
        assert resp.status_code == 200
        order = resp.json()["order"]
        assert order["discount_amount"] == 5.0  # 10% of 50
        assert order["total"] == 45.0

    def test_max_discount_in_admin_response(self, client, admin_token):
        resp = _create_coupon(
            client, admin_token,
            code="SHOW", discount_type="percent", discount_value=50,
            max_discount_amount=30,
        )
        assert resp.status_code == 201
        assert resp.json()["max_discount_amount"] == 30

    def test_max_discount_null_when_not_set(self, client, admin_token):
        resp = _create_coupon(client, admin_token, code="NOMAX")
        assert resp.status_code == 201
        assert resp.json()["max_discount_amount"] is None


# ============================================================
# Description Field
# ============================================================

class TestCouponDescription:
    def test_create_with_description(self, client, admin_token):
        resp = _create_coupon(
            client, admin_token,
            code="DESC", description="Save 10% on your order",
        )
        assert resp.status_code == 201
        assert resp.json()["description"] == "Save 10% on your order"

    def test_create_without_description(self, client, admin_token):
        resp = _create_coupon(client, admin_token, code="NODESC")
        assert resp.status_code == 201
        assert resp.json()["description"] is None

    def test_update_description(self, client, admin_token):
        create_resp = _create_coupon(client, admin_token)
        coupon_id = create_resp.json()["id"]

        resp = client.put(
            f"/api/admin/coupons/{coupon_id}",
            headers=_auth(admin_token),
            json={"description": "Updated desc"},
        )
        assert resp.status_code == 200
        assert resp.json()["description"] == "Updated desc"


# ============================================================
# Coupon Valid at Cart but Invalid at Checkout
# ============================================================

class TestCouponRevalidation:
    def test_coupon_deactivated_between_cart_and_checkout(
        self, client, admin_token, customer_token, product_a
    ):
        """Coupon applied to cart, then admin deactivates it before checkout."""
        create_resp = _create_coupon(client, admin_token, code="DEACT")
        coupon_id = create_resp.json()["id"]

        _add_to_cart(client, customer_token, product_a, quantity=1)
        _apply_coupon(client, customer_token, "DEACT")

        # Admin deactivates the coupon
        client.put(
            f"/api/admin/coupons/{coupon_id}",
            headers=_auth(admin_token),
            json={"is_active": False},
        )

        # Checkout should fail because coupon is now inactive
        resp = _checkout(client, customer_token)
        assert resp.status_code == 400
        assert "not active" in resp.json()["detail"].lower()

    def test_coupon_expired_between_cart_and_checkout(
        self, client, admin_token, customer_token, product_a
    ):
        """Coupon applied to cart, then it expires before checkout."""
        # Create coupon that expires very soon (already expired by checkout)
        past = (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()
        future = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        create_resp = _create_coupon(
            client, admin_token, code="EXPIRE",
            starts_at=None, ends_at=future,
        )
        coupon_id = create_resp.json()["id"]

        _add_to_cart(client, customer_token, product_a, quantity=1)
        _apply_coupon(client, customer_token, "EXPIRE")

        # Admin updates ends_at to the past (simulates expiry)
        client.put(
            f"/api/admin/coupons/{coupon_id}",
            headers=_auth(admin_token),
            json={"ends_at": past},
        )

        resp = _checkout(client, customer_token)
        assert resp.status_code == 400
        assert "expired" in resp.json()["detail"].lower()

    def test_coupon_usage_exhausted_between_cart_and_checkout(
        self, client, admin_token, customer_token, customer2_token, product_a
    ):
        """Coupon with max_uses=1 applied to two carts; first checkout wins."""
        _create_coupon(client, admin_token, code="RACE", max_uses=1)

        # Customer 1 applies coupon
        _add_to_cart(client, customer_token, product_a, quantity=1)
        _apply_coupon(client, customer_token, "RACE")

        # Customer 2 applies the same coupon (still valid at this point)
        _add_to_cart(client, customer2_token, product_a, quantity=1)
        _apply_coupon(client, customer2_token, "RACE")

        # Customer 1 checks out first — succeeds
        resp1 = _checkout(client, customer_token)
        assert resp1.status_code == 200

        # Customer 2 checks out — coupon is now exhausted
        resp2 = _checkout(client, customer2_token)
        assert resp2.status_code == 400
        assert "limit reached" in resp2.json()["detail"].lower()


# ============================================================
# Checkout without Coupon (no regression)
# ============================================================

class TestCheckoutNoCoupon:
    def test_checkout_without_coupon_still_works(
        self, client, admin_token, customer_token, product_a
    ):
        _add_to_cart(client, customer_token, product_a, quantity=2)
        resp = _checkout(client, customer_token)
        assert resp.status_code == 200
        order = resp.json()["order"]
        assert order["subtotal"] == 200.0
        assert order["discount_amount"] == 0.0
        assert order["total"] == 200.0
        assert order["coupon_code"] is None
