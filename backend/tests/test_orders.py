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


@pytest.fixture()
def use_failing_payment():
    """Swap the payment provider for one that always fails."""
    failing = SimulatedProvider(force_failure=True)
    app.dependency_overrides[get_payment_provider] = lambda: failing
    yield
    app.dependency_overrides.pop(get_payment_provider, None)


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
# Successful checkout
# ============================================================

class TestSuccessfulCheckout:
    def test_checkout_creates_paid_order(self, client, customer_token, product_a):
        _add_to_cart(client, customer_token, product_a, quantity=2)
        resp = _checkout(client, customer_token)

        assert resp.status_code == 200
        data = resp.json()
        assert data["order"]["status"] == "paid"
        assert float(data["order"]["total"]) == 199.98
        assert len(data["order"]["items"]) == 1
        assert data["order"]["items"][0]["quantity"] == 2
        assert float(data["order"]["items"][0]["unit_price"]) == 99.99
        assert float(data["order"]["items"][0]["subtotal"]) == 199.98
        assert "payment_message" in data

    def test_stock_decremented_after_checkout(self, client, customer_token, product_a):
        _add_to_cart(client, customer_token, product_a, quantity=3)
        _checkout(client, customer_token)

        assert _get_product_stock(client, "midnight-oud") == 7  # was 10

    def test_multi_item_checkout(self, client, customer_token, product_a, product_b):
        _add_to_cart(client, customer_token, product_a, quantity=1)
        _add_to_cart(client, customer_token, product_b, quantity=2)
        resp = _checkout(client, customer_token)

        data = resp.json()
        assert data["order"]["status"] == "paid"
        # 99.99 + (49.50 * 2) = 198.99
        assert float(data["order"]["total"]) == 198.99
        assert len(data["order"]["items"]) == 2

        assert _get_product_stock(client, "midnight-oud") == 9
        assert _get_product_stock(client, "citrus-breeze") == 1

    def test_order_snapshots_price_at_checkout_time(
        self, client, customer_token, admin_token, product_a
    ):
        _add_to_cart(client, customer_token, product_a, quantity=1)
        resp = _checkout(client, customer_token)
        order_price = float(resp.json()["order"]["items"][0]["unit_price"])

        # Change product price after checkout
        client.put(
            f"/api/admin/catalog/products/{product_a}",
            headers=_auth(admin_token),
            json={"price": 199.99},
        )

        # Order still has original price
        order_id = resp.json()["order"]["id"]
        order = client.get(f"/api/orders/{order_id}", headers=_auth(customer_token)).json()
        assert float(order["items"][0]["unit_price"]) == order_price


# ============================================================
# Cart finalization
# ============================================================

class TestCartFinalization:
    def test_cart_is_empty_after_checkout(self, client, customer_token, product_a):
        _add_to_cart(client, customer_token, product_a, quantity=1)
        _checkout(client, customer_token)

        cart = client.get("/api/cart", headers=_auth(customer_token)).json()
        assert cart["item_count"] == 0

    def test_user_gets_fresh_cart_after_checkout(self, client, customer_token, product_a):
        # First checkout
        _add_to_cart(client, customer_token, product_a, quantity=1)
        _checkout(client, customer_token)

        # New cart should be different
        cart_after = client.get("/api/cart", headers=_auth(customer_token)).json()
        assert cart_after["item_count"] == 0

        # Can add items to new cart
        _add_to_cart(client, customer_token, product_a, quantity=2)
        cart_after = client.get("/api/cart", headers=_auth(customer_token)).json()
        assert cart_after["item_count"] == 1
        assert cart_after["items"][0]["quantity"] == 2


# ============================================================
# Order history
# ============================================================

class TestOrderHistory:
    def test_list_orders(self, client, customer_token, product_a, product_b):
        # First order
        _add_to_cart(client, customer_token, product_a, quantity=1)
        _checkout(client, customer_token)

        # Second order
        _add_to_cart(client, customer_token, product_b, quantity=1)
        _checkout(client, customer_token)

        resp = client.get("/api/orders", headers=_auth(customer_token))
        assert resp.status_code == 200
        orders = resp.json()
        assert len(orders) == 2
        # Most recent first
        assert float(orders[0]["total"]) == 49.50
        assert float(orders[1]["total"]) == 99.99

    def test_get_order_by_id(self, client, customer_token, product_a):
        _add_to_cart(client, customer_token, product_a, quantity=1)
        checkout_resp = _checkout(client, customer_token)
        order_id = checkout_resp.json()["order"]["id"]

        resp = client.get(f"/api/orders/{order_id}", headers=_auth(customer_token))
        assert resp.status_code == 200
        assert resp.json()["id"] == order_id

    def test_cannot_see_other_users_order(self, client, customer_token, product_a):
        _add_to_cart(client, customer_token, product_a, quantity=1)
        checkout_resp = _checkout(client, customer_token)
        order_id = checkout_resp.json()["order"]["id"]

        # Second user
        client.post(
            "/api/auth/register",
            json={"email": "other@test.com", "password": "pass", "full_name": "Other"},
        )
        other = client.post(
            "/api/auth/login", json={"email": "other@test.com", "password": "pass"}
        )
        other_token = other.json()["access_token"]

        resp = client.get(f"/api/orders/{order_id}", headers=_auth(other_token))
        assert resp.status_code == 404


# ============================================================
# Insufficient stock
# ============================================================

class TestInsufficientStock:
    def test_checkout_fails_if_not_enough_stock(self, client, customer_token, product_b):
        # product_b has stock=3
        _add_to_cart(client, customer_token, product_b, quantity=5)
        resp = _checkout(client, customer_token)
        assert resp.status_code == 409
        assert "Insufficient stock" in resp.json()["detail"]

    def test_stock_unchanged_on_insufficient_stock(self, client, customer_token, product_b):
        _add_to_cart(client, customer_token, product_b, quantity=5)
        _checkout(client, customer_token)

        assert _get_product_stock(client, "citrus-breeze") == 3  # unchanged

    def test_partial_stock_failure_rolls_back_everything(
        self, client, customer_token, product_a, product_b
    ):
        # product_a has stock=10, product_b has stock=3
        _add_to_cart(client, customer_token, product_a, quantity=2)
        _add_to_cart(client, customer_token, product_b, quantity=5)  # exceeds stock
        resp = _checkout(client, customer_token)
        assert resp.status_code == 409

        # Both products should have original stock
        assert _get_product_stock(client, "midnight-oud") == 10
        assert _get_product_stock(client, "citrus-breeze") == 3


# ============================================================
# Empty cart
# ============================================================

class TestEmptyCart:
    def test_checkout_empty_cart_fails(self, client, customer_token):
        resp = _checkout(client, customer_token)
        assert resp.status_code == 400
        assert "empty" in resp.json()["detail"].lower()


# ============================================================
# Payment failure
# ============================================================

class TestPaymentFailure:
    def test_payment_failure_creates_failed_order(
        self, client, customer_token, product_a, use_failing_payment
    ):
        _add_to_cart(client, customer_token, product_a, quantity=2)
        resp = _checkout(client, customer_token)

        assert resp.status_code == 200
        data = resp.json()
        assert data["order"]["status"] == "failed"
        assert "declined" in data["payment_message"].lower()

    def test_stock_restored_on_payment_failure(
        self, client, customer_token, product_a, use_failing_payment
    ):
        _add_to_cart(client, customer_token, product_a, quantity=3)
        _checkout(client, customer_token)

        assert _get_product_stock(client, "midnight-oud") == 10  # restored

    def test_cart_stays_active_on_payment_failure(
        self, client, customer_token, product_a, use_failing_payment
    ):
        _add_to_cart(client, customer_token, product_a, quantity=2)
        _checkout(client, customer_token)

        # Cart should still be active with items
        cart = client.get("/api/cart", headers=_auth(customer_token)).json()
        assert cart["item_count"] == 1
        assert cart["items"][0]["quantity"] == 2

    def test_can_retry_after_payment_failure(self, client, customer_token, product_a):
        _add_to_cart(client, customer_token, product_a, quantity=2)

        # First attempt fails
        failing = SimulatedProvider(force_failure=True)
        app.dependency_overrides[get_payment_provider] = lambda: failing
        resp1 = _checkout(client, customer_token)
        assert resp1.json()["order"]["status"] == "failed"

        # Second attempt succeeds (restore default provider)
        app.dependency_overrides.pop(get_payment_provider, None)
        resp2 = _checkout(client, customer_token)
        assert resp2.json()["order"]["status"] == "paid"

        # Stock decremented only once
        assert _get_product_stock(client, "midnight-oud") == 8

        # Order history has both
        orders = client.get("/api/orders", headers=_auth(customer_token)).json()
        assert len(orders) == 2


# ============================================================
# Double checkout protection
# ============================================================

class TestDoubleCheckout:
    def test_double_checkout_same_cart_fails(self, client, customer_token, product_a):
        _add_to_cart(client, customer_token, product_a, quantity=1)
        resp1 = _checkout(client, customer_token)
        assert resp1.status_code == 200
        assert resp1.json()["order"]["status"] == "paid"

        # Second checkout: cart is already checked out, user gets empty new cart
        resp2 = _checkout(client, customer_token)
        assert resp2.status_code == 400
        assert "empty" in resp2.json()["detail"].lower()

    def test_stock_not_double_decremented(self, client, customer_token, product_a):
        _add_to_cart(client, customer_token, product_a, quantity=2)
        _checkout(client, customer_token)

        # Try again — should fail, stock should still be 8
        _checkout(client, customer_token)
        assert _get_product_stock(client, "midnight-oud") == 8


# ============================================================
# Edge cases
# ============================================================

class TestEdgeCases:
    def test_checkout_with_inactive_product_fails(
        self, client, customer_token, admin_token, product_a
    ):
        _add_to_cart(client, customer_token, product_a, quantity=1)

        # Deactivate product after adding to cart
        client.put(
            f"/api/admin/catalog/products/{product_a}",
            headers=_auth(admin_token),
            json={"is_active": False},
        )

        resp = _checkout(client, customer_token)
        assert resp.status_code == 409
        assert "no longer available" in resp.json()["detail"].lower()

    def test_checkout_exact_stock_succeeds(self, client, customer_token, product_b):
        # product_b has stock=3, buy exactly 3
        _add_to_cart(client, customer_token, product_b, quantity=3)
        resp = _checkout(client, customer_token)
        assert resp.status_code == 200
        assert resp.json()["order"]["status"] == "paid"
        assert _get_product_stock(client, "citrus-breeze") == 0

    def test_unauthenticated_checkout_fails(self, client):
        resp = client.post("/api/orders/checkout")
        assert resp.status_code == 401

    def test_order_total_calculation_precision(
        self, client, customer_token, product_a, product_b
    ):
        # 99.99 * 3 = 299.97
        # 49.50 * 2 = 99.00
        # total = 398.97
        _add_to_cart(client, customer_token, product_a, quantity=3)
        _add_to_cart(client, customer_token, product_b, quantity=2)
        resp = _checkout(client, customer_token)
        assert float(resp.json()["order"]["total"]) == 398.97
