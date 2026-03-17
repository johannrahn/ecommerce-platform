import pytest

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
def category_id(client, admin_token):
    resp = client.post(
        "/api/admin/catalog/categories",
        headers=_auth(admin_token),
        json={"name": "Perfume", "slug": "perfume"},
    )
    return resp.json()["id"]


def _create_product(client, admin_token, category_id, name, slug, price, stock):
    resp = client.post(
        "/api/admin/catalog/products",
        headers=_auth(admin_token),
        json={
            "name": name,
            "slug": slug,
            "price": price,
            "stock": stock,
            "category_id": category_id,
        },
    )
    return resp.json()["id"]


@pytest.fixture()
def product_a(client, admin_token, category_id):
    """Product with stock=10, price=99.99"""
    return _create_product(client, admin_token, category_id, "Midnight Oud", "midnight-oud", 99.99, 10)


@pytest.fixture()
def product_b(client, admin_token, category_id):
    """Product with stock=3, price=49.50"""
    return _create_product(client, admin_token, category_id, "Citrus Breeze", "citrus-breeze", 49.50, 3)


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _add_to_cart(client, token, product_id, quantity=1):
    return client.post(
        "/api/cart/items",
        headers=_auth(token),
        json={"product_id": product_id, "quantity": quantity},
    )


def _checkout(client, token):
    return client.post("/api/orders/checkout", headers=_auth(token))


def _get_product_stock(client, slug):
    resp = client.get(f"/api/catalog/products/{slug}")
    return resp.json()["stock"]


# ============================================================
# Admin order listing
# ============================================================

class TestAdminListOrders:
    def test_admin_lists_all_orders(self, client, admin_token, customer_token, product_a):
        _add_to_cart(client, customer_token, product_a, quantity=1)
        _checkout(client, customer_token)

        resp = client.get("/api/admin/orders", headers=_auth(admin_token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["status"] == "paid"

    def test_admin_lists_orders_from_multiple_users(
        self, client, admin_token, customer_token, product_a
    ):
        # Customer 1 checkout
        _add_to_cart(client, customer_token, product_a, quantity=1)
        _checkout(client, customer_token)

        # Customer 2 checkout
        client.post(
            "/api/auth/register",
            json={"email": "cust2@test.com", "password": "pass", "full_name": "Cust2"},
        )
        token2 = client.post(
            "/api/auth/login", json={"email": "cust2@test.com", "password": "pass"}
        ).json()["access_token"]
        _add_to_cart(client, token2, product_a, quantity=1)
        _checkout(client, token2)

        resp = client.get("/api/admin/orders", headers=_auth(admin_token))
        assert resp.json()["total"] == 2

    def test_admin_empty_order_list(self, client, admin_token):
        resp = client.get("/api/admin/orders", headers=_auth(admin_token))
        assert resp.status_code == 200
        assert resp.json()["items"] == []
        assert resp.json()["total"] == 0


# ============================================================
# Status filtering
# ============================================================

class TestAdminFilterOrders:
    def test_filter_by_paid_status(self, client, admin_token, customer_token, product_a):
        _add_to_cart(client, customer_token, product_a, quantity=1)
        _checkout(client, customer_token)

        resp = client.get("/api/admin/orders?status=paid", headers=_auth(admin_token))
        assert resp.status_code == 200
        assert resp.json()["total"] == 1

        resp = client.get("/api/admin/orders?status=failed", headers=_auth(admin_token))
        assert resp.json()["total"] == 0

    def test_filter_by_failed_status(self, client, admin_token, customer_token, product_a):
        failing = SimulatedProvider(force_failure=True)
        app.dependency_overrides[get_payment_provider] = lambda: failing

        _add_to_cart(client, customer_token, product_a, quantity=1)
        _checkout(client, customer_token)

        app.dependency_overrides.pop(get_payment_provider, None)

        resp = client.get("/api/admin/orders?status=failed", headers=_auth(admin_token))
        assert resp.json()["total"] == 1

        resp = client.get("/api/admin/orders?status=paid", headers=_auth(admin_token))
        assert resp.json()["total"] == 0


# ============================================================
# Admin get order detail
# ============================================================

class TestAdminGetOrder:
    def test_admin_gets_order_detail(self, client, admin_token, customer_token, product_a):
        _add_to_cart(client, customer_token, product_a, quantity=2)
        checkout_resp = _checkout(client, customer_token)
        order_id = checkout_resp.json()["order"]["id"]

        resp = client.get(f"/api/admin/orders/{order_id}", headers=_auth(admin_token))
        assert resp.status_code == 200
        assert resp.json()["id"] == order_id
        assert len(resp.json()["items"]) == 1
        assert resp.json()["items"][0]["quantity"] == 2

    def test_admin_gets_nonexistent_order(self, client, admin_token):
        resp = client.get("/api/admin/orders/fake-id", headers=_auth(admin_token))
        assert resp.status_code == 404


# ============================================================
# Admin cancel order + stock restoration
# ============================================================

class TestAdminCancelOrder:
    def test_cancel_paid_order(self, client, admin_token, customer_token, product_a):
        _add_to_cart(client, customer_token, product_a, quantity=3)
        checkout_resp = _checkout(client, customer_token)
        order_id = checkout_resp.json()["order"]["id"]

        resp = client.post(f"/api/admin/orders/{order_id}/cancel", headers=_auth(admin_token))
        assert resp.status_code == 200
        assert resp.json()["status"] == "cancelled"

    def test_cancel_restores_stock(self, client, admin_token, customer_token, product_a):
        assert _get_product_stock(client, "midnight-oud") == 10

        _add_to_cart(client, customer_token, product_a, quantity=3)
        checkout_resp = _checkout(client, customer_token)
        order_id = checkout_resp.json()["order"]["id"]

        assert _get_product_stock(client, "midnight-oud") == 7

        client.post(f"/api/admin/orders/{order_id}/cancel", headers=_auth(admin_token))
        assert _get_product_stock(client, "midnight-oud") == 10

    def test_cancel_multi_item_restores_all_stock(
        self, client, admin_token, customer_token, product_a, product_b
    ):
        _add_to_cart(client, customer_token, product_a, quantity=2)
        _add_to_cart(client, customer_token, product_b, quantity=1)
        checkout_resp = _checkout(client, customer_token)
        order_id = checkout_resp.json()["order"]["id"]

        assert _get_product_stock(client, "midnight-oud") == 8
        assert _get_product_stock(client, "citrus-breeze") == 2

        client.post(f"/api/admin/orders/{order_id}/cancel", headers=_auth(admin_token))
        assert _get_product_stock(client, "midnight-oud") == 10
        assert _get_product_stock(client, "citrus-breeze") == 3

    def test_cannot_cancel_failed_order(self, client, admin_token, customer_token, product_a):
        failing = SimulatedProvider(force_failure=True)
        app.dependency_overrides[get_payment_provider] = lambda: failing

        _add_to_cart(client, customer_token, product_a, quantity=1)
        checkout_resp = _checkout(client, customer_token)
        order_id = checkout_resp.json()["order"]["id"]

        app.dependency_overrides.pop(get_payment_provider, None)

        resp = client.post(f"/api/admin/orders/{order_id}/cancel", headers=_auth(admin_token))
        assert resp.status_code == 409
        assert "Only paid orders" in resp.json()["detail"]

    def test_cannot_cancel_already_cancelled_order(
        self, client, admin_token, customer_token, product_a
    ):
        _add_to_cart(client, customer_token, product_a, quantity=1)
        checkout_resp = _checkout(client, customer_token)
        order_id = checkout_resp.json()["order"]["id"]

        # First cancel succeeds
        resp1 = client.post(f"/api/admin/orders/{order_id}/cancel", headers=_auth(admin_token))
        assert resp1.status_code == 200

        # Second cancel fails
        resp2 = client.post(f"/api/admin/orders/{order_id}/cancel", headers=_auth(admin_token))
        assert resp2.status_code == 409

    def test_cancel_nonexistent_order(self, client, admin_token):
        resp = client.post("/api/admin/orders/fake-id/cancel", headers=_auth(admin_token))
        assert resp.status_code == 404


# ============================================================
# Stock update validation (via existing product update endpoint)
# ============================================================

class TestAdminStockUpdate:
    def test_admin_updates_stock(self, client, admin_token, product_a):
        resp = client.put(
            f"/api/admin/catalog/products/{product_a}",
            headers=_auth(admin_token),
            json={"stock": 50},
        )
        assert resp.status_code == 200
        assert resp.json()["stock"] == 50
        assert _get_product_stock(client, "midnight-oud") == 50

    def test_stock_cannot_be_negative(self, client, admin_token, product_a):
        resp = client.put(
            f"/api/admin/catalog/products/{product_a}",
            headers=_auth(admin_token),
            json={"stock": -1},
        )
        assert resp.status_code == 422  # Pydantic validation

    def test_admin_deactivates_product(self, client, admin_token, product_a):
        resp = client.put(
            f"/api/admin/catalog/products/{product_a}",
            headers=_auth(admin_token),
            json={"is_active": False},
        )
        assert resp.status_code == 200
        assert resp.json()["is_active"] is False

        # Product no longer visible in public listing
        public_resp = client.get("/api/catalog/products")
        slugs = [p["slug"] for p in public_resp.json()["items"]]
        assert "midnight-oud" not in slugs

    def test_admin_reactivates_product(self, client, admin_token, product_a):
        client.put(
            f"/api/admin/catalog/products/{product_a}",
            headers=_auth(admin_token),
            json={"is_active": False},
        )
        resp = client.put(
            f"/api/admin/catalog/products/{product_a}",
            headers=_auth(admin_token),
            json={"is_active": True},
        )
        assert resp.status_code == 200
        assert resp.json()["is_active"] is True


# ============================================================
# Authorization protection
# ============================================================

class TestAdminOrderAuth:
    def test_customer_cannot_list_admin_orders(self, client, customer_token):
        resp = client.get("/api/admin/orders", headers=_auth(customer_token))
        assert resp.status_code == 403

    def test_customer_cannot_cancel_order(self, client, customer_token, admin_token, product_a):
        _add_to_cart(client, customer_token, product_a, quantity=1)
        checkout_resp = _checkout(client, customer_token)
        order_id = checkout_resp.json()["order"]["id"]

        resp = client.post(
            f"/api/admin/orders/{order_id}/cancel", headers=_auth(customer_token)
        )
        assert resp.status_code == 403

    def test_unauthenticated_cannot_access_admin_orders(self, client):
        resp = client.get("/api/admin/orders")
        assert resp.status_code == 401

    def test_customer_cannot_get_admin_order_detail(self, client, customer_token):
        resp = client.get("/api/admin/orders/some-id", headers=_auth(customer_token))
        assert resp.status_code == 403
