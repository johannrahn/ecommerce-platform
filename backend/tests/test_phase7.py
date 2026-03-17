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
# Admin Coupon CRUD
# ============================================================

class TestAdminCouponCRUD:
    def test_create_coupon(self, client, admin_token):
        resp = _create_coupon(client, admin_token)
        assert resp.status_code == 201
        data = resp.json()
        assert data["code"] == "SAVE10"
        assert data["discount_type"] == "percent"
        assert data["discount_value"] == 10
        assert data["used_count"] == 0
        assert data["is_active"] is True

    def test_create_fixed_coupon(self, client, admin_token):
        resp = _create_coupon(
            client, admin_token,
            code="FLAT20", discount_type="fixed", discount_value=20,
            minimum_order_amount=50,
        )
        assert resp.status_code == 201
        assert resp.json()["discount_type"] == "fixed"
        assert resp.json()["minimum_order_amount"] == 50

    def test_create_duplicate_code_fails(self, client, admin_token):
        _create_coupon(client, admin_token)
        resp = _create_coupon(client, admin_token)
        assert resp.status_code == 409

    def test_list_coupons(self, client, admin_token):
        _create_coupon(client, admin_token, code="A1")
        _create_coupon(client, admin_token, code="A2")
        resp = client.get("/api/admin/coupons", headers=_auth(admin_token))
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_get_coupon(self, client, admin_token):
        create_resp = _create_coupon(client, admin_token)
        coupon_id = create_resp.json()["id"]
        resp = client.get(f"/api/admin/coupons/{coupon_id}", headers=_auth(admin_token))
        assert resp.status_code == 200
        assert resp.json()["code"] == "SAVE10"

    def test_update_coupon(self, client, admin_token):
        create_resp = _create_coupon(client, admin_token)
        coupon_id = create_resp.json()["id"]
        resp = client.put(
            f"/api/admin/coupons/{coupon_id}",
            headers=_auth(admin_token),
            json={"discount_value": 25, "is_active": False},
        )
        assert resp.status_code == 200
        assert resp.json()["discount_value"] == 25
        assert resp.json()["is_active"] is False

    def test_update_coupon_code_uniqueness(self, client, admin_token):
        _create_coupon(client, admin_token, code="FIRST")
        resp2 = _create_coupon(client, admin_token, code="SECOND")
        coupon_id = resp2.json()["id"]
        resp = client.put(
            f"/api/admin/coupons/{coupon_id}",
            headers=_auth(admin_token),
            json={"code": "FIRST"},
        )
        assert resp.status_code == 409

    def test_get_nonexistent_coupon(self, client, admin_token):
        resp = client.get("/api/admin/coupons/fake-id", headers=_auth(admin_token))
        assert resp.status_code == 404

    def test_customer_cannot_access_admin_coupons(self, client, customer_token):
        resp = client.get("/api/admin/coupons", headers=_auth(customer_token))
        assert resp.status_code == 403


# ============================================================
# Checkout with Coupon — Percent Discount
# ============================================================

class TestCheckoutWithPercentCoupon:
    def test_percent_discount_applied(self, client, admin_token, customer_token, product_a):
        _create_coupon(client, admin_token, code="SAVE10", discount_type="percent", discount_value=10)
        _add_to_cart(client, customer_token, product_a, quantity=2)  # subtotal=200
        _apply_coupon(client, customer_token, "SAVE10")

        resp = _checkout(client, customer_token)
        assert resp.status_code == 200
        order = resp.json()["order"]
        assert order["subtotal"] == 200.0
        assert order["discount_amount"] == 20.0
        assert order["total"] == 180.0
        assert order["coupon_code"] == "SAVE10"

    def test_100_percent_discount(self, client, admin_token, customer_token, product_a):
        _create_coupon(client, admin_token, code="FREE", discount_type="percent", discount_value=100)
        _add_to_cart(client, customer_token, product_a, quantity=1)  # subtotal=100
        _apply_coupon(client, customer_token, "FREE")

        resp = _checkout(client, customer_token)
        assert resp.status_code == 200
        order = resp.json()["order"]
        assert order["discount_amount"] == 100.0
        assert order["total"] == 0.0


# ============================================================
# Checkout with Coupon — Fixed Discount
# ============================================================

class TestCheckoutWithFixedCoupon:
    def test_fixed_discount_applied(self, client, admin_token, customer_token, product_a):
        _create_coupon(client, admin_token, code="FLAT15", discount_type="fixed", discount_value=15)
        _add_to_cart(client, customer_token, product_a, quantity=1)  # subtotal=100
        _apply_coupon(client, customer_token, "FLAT15")

        resp = _checkout(client, customer_token)
        assert resp.status_code == 200
        order = resp.json()["order"]
        assert order["subtotal"] == 100.0
        assert order["discount_amount"] == 15.0
        assert order["total"] == 85.0

    def test_fixed_discount_capped_at_subtotal(self, client, admin_token, customer_token, product_b):
        """Fixed discount larger than subtotal: total should be 0, not negative."""
        _create_coupon(client, admin_token, code="BIG", discount_type="fixed", discount_value=999)
        _add_to_cart(client, customer_token, product_b, quantity=1)  # subtotal=50
        _apply_coupon(client, customer_token, "BIG")

        resp = _checkout(client, customer_token)
        assert resp.status_code == 200
        order = resp.json()["order"]
        assert order["discount_amount"] == 50.0  # capped at subtotal
        assert order["total"] == 0.0


# ============================================================
# Checkout without Coupon — backward compatible
# ============================================================

class TestCheckoutWithoutCoupon:
    def test_no_coupon_works(self, client, admin_token, customer_token, product_a):
        _add_to_cart(client, customer_token, product_a, quantity=2)
        resp = _checkout(client, customer_token)
        assert resp.status_code == 200
        order = resp.json()["order"]
        assert order["subtotal"] == 200.0
        assert order["discount_amount"] == 0.0
        assert order["total"] == 200.0
        assert order["coupon_code"] is None


# ============================================================
# Coupon Validation Rules
# ============================================================

class TestCouponValidation:
    def test_invalid_code_at_cart(self, client, customer_token, product_a):
        _add_to_cart(client, customer_token, product_a, quantity=1)
        resp = _apply_coupon(client, customer_token, "DOESNOTEXIST")
        assert resp.status_code == 404

    def test_inactive_coupon(self, client, admin_token, customer_token, product_a):
        _create_coupon(client, admin_token, code="OFF", is_active=False)
        _add_to_cart(client, customer_token, product_a, quantity=1)
        resp = _apply_coupon(client, customer_token, "OFF")
        assert resp.status_code == 400
        assert "not active" in resp.json()["detail"].lower()

    def test_coupon_not_yet_valid(self, client, admin_token, customer_token, product_a):
        future = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
        _create_coupon(client, admin_token, code="FUTURE", starts_at=future)
        _add_to_cart(client, customer_token, product_a, quantity=1)
        resp = _apply_coupon(client, customer_token, "FUTURE")
        assert resp.status_code == 400
        assert "not yet valid" in resp.json()["detail"].lower()

    def test_coupon_expired(self, client, admin_token, customer_token, product_a):
        past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        _create_coupon(client, admin_token, code="EXPIRED", ends_at=past)
        _add_to_cart(client, customer_token, product_a, quantity=1)
        resp = _apply_coupon(client, customer_token, "EXPIRED")
        assert resp.status_code == 400
        assert "expired" in resp.json()["detail"].lower()

    def test_coupon_max_uses_reached(self, client, admin_token, customer_token, product_a):
        _create_coupon(client, admin_token, code="ONCE", max_uses=1)
        # First checkout uses the coupon
        _add_to_cart(client, customer_token, product_a, quantity=1)
        _apply_coupon(client, customer_token, "ONCE")
        resp1 = _checkout(client, customer_token)
        assert resp1.status_code == 200

        # Second apply with same coupon should fail (usage limit reached)
        _add_to_cart(client, customer_token, product_a, quantity=1)
        resp2 = _apply_coupon(client, customer_token, "ONCE")
        assert resp2.status_code == 400
        assert "limit reached" in resp2.json()["detail"].lower()

    def test_minimum_order_amount_checked_at_checkout(
        self, client, admin_token, customer_token, product_b
    ):
        """minimum_order_amount is only checked at checkout, not at cart apply."""
        _create_coupon(
            client, admin_token,
            code="MIN200", discount_type="fixed", discount_value=10,
            minimum_order_amount=200,
        )
        _add_to_cart(client, customer_token, product_b, quantity=1)  # subtotal=50
        # Apply to cart succeeds (minimum not checked at cart time)
        apply_resp = _apply_coupon(client, customer_token, "MIN200")
        assert apply_resp.status_code == 200

        # Checkout fails because subtotal < minimum
        resp = _checkout(client, customer_token)
        assert resp.status_code == 400
        assert "minimum" in resp.json()["detail"].lower()

    def test_one_per_user(self, client, admin_token, customer_token, product_a):
        _create_coupon(client, admin_token, code="SINGLE", one_per_user=True)
        # First use succeeds
        _add_to_cart(client, customer_token, product_a, quantity=1)
        _apply_coupon(client, customer_token, "SINGLE")
        resp1 = _checkout(client, customer_token)
        assert resp1.status_code == 200

        # Second use by same user fails at apply
        _add_to_cart(client, customer_token, product_a, quantity=1)
        resp2 = _apply_coupon(client, customer_token, "SINGLE")
        assert resp2.status_code == 400
        assert "already used" in resp2.json()["detail"].lower()

    def test_one_per_user_different_users(
        self, client, admin_token, customer_token, customer2_token, product_a
    ):
        _create_coupon(client, admin_token, code="SHARED", one_per_user=True, max_uses=10)
        # User 1 uses coupon
        _add_to_cart(client, customer_token, product_a, quantity=1)
        _apply_coupon(client, customer_token, "SHARED")
        resp1 = _checkout(client, customer_token)
        assert resp1.status_code == 200

        # User 2 can still use same coupon
        _add_to_cart(client, customer2_token, product_a, quantity=1)
        _apply_coupon(client, customer2_token, "SHARED")
        resp2 = _checkout(client, customer2_token)
        assert resp2.status_code == 200


# ============================================================
# Coupon usage count tracking
# ============================================================

class TestCouponUsageCount:
    def test_used_count_increments(self, client, admin_token, customer_token, product_a):
        create_resp = _create_coupon(client, admin_token, code="COUNT", max_uses=10)
        coupon_id = create_resp.json()["id"]
        assert create_resp.json()["used_count"] == 0

        _add_to_cart(client, customer_token, product_a, quantity=1)
        _apply_coupon(client, customer_token, "COUNT")
        _checkout(client, customer_token)

        detail = client.get(f"/api/admin/coupons/{coupon_id}", headers=_auth(admin_token))
        assert detail.json()["used_count"] == 1

    def test_failed_payment_does_not_increment_usage(
        self, client, admin_token, customer_token, product_a
    ):
        create_resp = _create_coupon(client, admin_token, code="NOFAIL")
        coupon_id = create_resp.json()["id"]

        failing = SimulatedProvider(force_failure=True)
        app.dependency_overrides[get_payment_provider] = lambda: failing

        _add_to_cart(client, customer_token, product_a, quantity=1)
        _apply_coupon(client, customer_token, "NOFAIL")
        resp = _checkout(client, customer_token)
        assert resp.json()["order"]["status"] == "failed"

        app.dependency_overrides.pop(get_payment_provider, None)

        detail = client.get(f"/api/admin/coupons/{coupon_id}", headers=_auth(admin_token))
        assert detail.json()["used_count"] == 0


# ============================================================
# Order response shape includes new fields
# ============================================================

class TestOrderResponseShape:
    def test_order_list_includes_discount_fields(self, client, admin_token, customer_token, product_a):
        _create_coupon(client, admin_token, code="SHAPE", discount_type="fixed", discount_value=5)
        _add_to_cart(client, customer_token, product_a, quantity=1)
        _apply_coupon(client, customer_token, "SHAPE")
        _checkout(client, customer_token)

        resp = client.get("/api/orders", headers=_auth(customer_token))
        assert resp.status_code == 200
        order = resp.json()[0]
        assert "subtotal" in order
        assert "discount_amount" in order
        assert "coupon_code" in order
        assert order["coupon_code"] == "SHAPE"

    def test_admin_order_detail_includes_discount_fields(
        self, client, admin_token, customer_token, product_a
    ):
        _add_to_cart(client, customer_token, product_a, quantity=1)
        checkout_resp = _checkout(client, customer_token)
        order_id = checkout_resp.json()["order"]["id"]

        resp = client.get(f"/api/admin/orders/{order_id}", headers=_auth(admin_token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["subtotal"] == 100.0
        assert data["discount_amount"] == 0.0
        assert data["coupon_code"] is None
