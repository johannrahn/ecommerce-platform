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
    """Product with stock=5, price=49.50"""
    return _create_product(client, admin_token, category_id, "Citrus Breeze", "citrus-breeze", 49.50, 5)


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _add_to_cart(client, token, product_id, quantity=1):
    return client.post(
        "/api/cart/items",
        headers=_auth(token),
        json={"product_id": product_id, "quantity": quantity},
    )


def _checkout(client, token, idempotency_key=None):
    headers = _auth(token)
    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key
    return client.post("/api/orders/checkout", headers=headers)


def _get_product_stock(client, slug):
    resp = client.get(f"/api/catalog/products/{slug}")
    return resp.json()["stock"]


# ============================================================
# Order Pagination
# ============================================================

class TestOrderPagination:
    def _create_orders(self, client, customer_token, product_a, count):
        """Create multiple paid orders."""
        for _ in range(count):
            _add_to_cart(client, customer_token, product_a, quantity=1)
            _checkout(client, customer_token)

    def test_default_pagination(self, client, admin_token, customer_token, product_a):
        self._create_orders(client, customer_token, product_a, 3)

        resp = client.get("/api/admin/orders", headers=_auth(admin_token))
        data = resp.json()
        assert data["total"] == 3
        assert data["limit"] == 20
        assert data["offset"] == 0
        assert len(data["items"]) == 3

    def test_limit_offset(self, client, admin_token, customer_token, product_a):
        self._create_orders(client, customer_token, product_a, 5)

        resp = client.get("/api/admin/orders?limit=2&offset=0", headers=_auth(admin_token))
        data = resp.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2
        assert data["limit"] == 2
        assert data["offset"] == 0

    def test_offset_skips_items(self, client, admin_token, customer_token, product_a):
        self._create_orders(client, customer_token, product_a, 5)

        resp = client.get("/api/admin/orders?limit=2&offset=3", headers=_auth(admin_token))
        data = resp.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2  # items 4 and 5

    def test_offset_beyond_total(self, client, admin_token, customer_token, product_a):
        self._create_orders(client, customer_token, product_a, 2)

        resp = client.get("/api/admin/orders?limit=20&offset=10", headers=_auth(admin_token))
        data = resp.json()
        assert data["total"] == 2
        assert len(data["items"]) == 0


# ============================================================
# Order Filtering
# ============================================================

class TestOrderFiltering:
    def test_filter_by_user_id(
        self, client, admin_token, customer_token, customer2_token, product_a
    ):
        # Customer 1 creates an order
        _add_to_cart(client, customer_token, product_a, quantity=1)
        resp1 = _checkout(client, customer_token)
        user1_order_id = resp1.json()["order"]["id"]

        # Customer 2 creates an order
        _add_to_cart(client, customer2_token, product_a, quantity=1)
        _checkout(client, customer2_token)

        # Get user_id from order
        order_detail = client.get(
            f"/api/admin/orders/{user1_order_id}", headers=_auth(admin_token)
        ).json()

        # Need user_id — get it from the customer profile
        profile = client.get("/api/users/me", headers=_auth(customer_token)).json()
        user_id = profile["id"]

        resp = client.get(
            f"/api/admin/orders?user_id={user_id}", headers=_auth(admin_token)
        )
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["id"] == user1_order_id

    def test_filter_by_created_after(
        self, client, admin_token, customer_token, product_a
    ):
        _add_to_cart(client, customer_token, product_a, quantity=1)
        _checkout(client, customer_token)

        # Filter with a date far in the past — should include the order
        resp = client.get(
            "/api/admin/orders?created_after=2020-01-01T00:00:00",
            headers=_auth(admin_token),
        )
        assert resp.json()["total"] == 1

        # Filter with a date in the future — should exclude all
        resp = client.get(
            "/api/admin/orders?created_after=2099-01-01T00:00:00",
            headers=_auth(admin_token),
        )
        assert resp.json()["total"] == 0

    def test_filter_by_created_before(
        self, client, admin_token, customer_token, product_a
    ):
        _add_to_cart(client, customer_token, product_a, quantity=1)
        _checkout(client, customer_token)

        # Filter with a date in the future — should include the order
        resp = client.get(
            "/api/admin/orders?created_before=2099-01-01T00:00:00",
            headers=_auth(admin_token),
        )
        assert resp.json()["total"] == 1

        # Filter with a date far in the past — should exclude all
        resp = client.get(
            "/api/admin/orders?created_before=2020-01-01T00:00:00",
            headers=_auth(admin_token),
        )
        assert resp.json()["total"] == 0

    def test_combined_filters(
        self, client, admin_token, customer_token, product_a
    ):
        _add_to_cart(client, customer_token, product_a, quantity=1)
        _checkout(client, customer_token)

        resp = client.get(
            "/api/admin/orders?status=paid&created_after=2020-01-01T00:00:00&limit=5",
            headers=_auth(admin_token),
        )
        data = resp.json()
        assert data["total"] == 1
        assert data["limit"] == 5


# ============================================================
# Idempotency
# ============================================================

class TestIdempotency:
    def test_same_key_returns_same_order(
        self, client, customer_token, product_a
    ):
        _add_to_cart(client, customer_token, product_a, quantity=2)

        resp1 = _checkout(client, customer_token, idempotency_key="checkout-abc-123")
        assert resp1.status_code == 200
        order_id_1 = resp1.json()["order"]["id"]
        assert resp1.json()["order"]["status"] == "paid"

        # Same key again — should return the same order without re-processing
        resp2 = _checkout(client, customer_token, idempotency_key="checkout-abc-123")
        assert resp2.status_code == 200
        order_id_2 = resp2.json()["order"]["id"]
        assert order_id_1 == order_id_2
        assert "already processed" in resp2.json()["payment_message"].lower()

    def test_idempotency_does_not_double_decrement_stock(
        self, client, customer_token, product_a
    ):
        assert _get_product_stock(client, "midnight-oud") == 10

        _add_to_cart(client, customer_token, product_a, quantity=3)
        _checkout(client, customer_token, idempotency_key="key-stock-test")

        assert _get_product_stock(client, "midnight-oud") == 7

        # Replay with same key
        _checkout(client, customer_token, idempotency_key="key-stock-test")

        # Stock should still be 7, not 4
        assert _get_product_stock(client, "midnight-oud") == 7

    def test_different_key_creates_new_order(
        self, client, customer_token, product_a
    ):
        _add_to_cart(client, customer_token, product_a, quantity=1)
        resp1 = _checkout(client, customer_token, idempotency_key="key-1")
        order_id_1 = resp1.json()["order"]["id"]

        # New cart, new order, different key
        _add_to_cart(client, customer_token, product_a, quantity=1)
        resp2 = _checkout(client, customer_token, idempotency_key="key-2")
        order_id_2 = resp2.json()["order"]["id"]

        assert order_id_1 != order_id_2

    def test_no_key_works_as_before(self, client, customer_token, product_a):
        _add_to_cart(client, customer_token, product_a, quantity=1)
        resp = _checkout(client, customer_token)  # no idempotency key
        assert resp.status_code == 200
        assert resp.json()["order"]["status"] == "paid"

    def test_idempotency_key_is_per_user(
        self, client, customer_token, customer2_token, product_a
    ):
        # User 1 uses key "shared-key"
        _add_to_cart(client, customer_token, product_a, quantity=1)
        resp1 = _checkout(client, customer_token, idempotency_key="shared-key")
        order_id_1 = resp1.json()["order"]["id"]

        # User 2 uses same key "shared-key" — should create a different order
        _add_to_cart(client, customer2_token, product_a, quantity=1)
        resp2 = _checkout(client, customer2_token, idempotency_key="shared-key")
        order_id_2 = resp2.json()["order"]["id"]

        assert order_id_1 != order_id_2

    def test_failed_payment_is_also_idempotent(self, client, customer_token, product_a):
        """A failed payment is a completed operation. Replaying the same key
        returns the same failed order without retrying payment."""
        failing = SimulatedProvider(force_failure=True)
        app.dependency_overrides[get_payment_provider] = lambda: failing

        _add_to_cart(client, customer_token, product_a, quantity=2)
        resp1 = _checkout(client, customer_token, idempotency_key="fail-key")
        assert resp1.json()["order"]["status"] == "failed"
        order_id = resp1.json()["order"]["id"]

        app.dependency_overrides.pop(get_payment_provider, None)

        # Replay with same key — should return the SAME failed order,
        # NOT retry with the (now-working) payment provider
        resp2 = _checkout(client, customer_token, idempotency_key="fail-key")
        assert resp2.json()["order"]["id"] == order_id
        assert resp2.json()["order"]["status"] == "failed"
        assert "already processed" in resp2.json()["payment_message"].lower()

    def test_failed_payment_stock_not_double_restored(self, client, customer_token, product_a):
        """Replaying idempotency key after failed payment must not touch stock."""
        assert _get_product_stock(client, "midnight-oud") == 10

        failing = SimulatedProvider(force_failure=True)
        app.dependency_overrides[get_payment_provider] = lambda: failing

        _add_to_cart(client, customer_token, product_a, quantity=3)
        _checkout(client, customer_token, idempotency_key="fail-stock-key")
        assert _get_product_stock(client, "midnight-oud") == 10  # restored on failure

        app.dependency_overrides.pop(get_payment_provider, None)

        # Replay — stock must remain 10, not 13
        _checkout(client, customer_token, idempotency_key="fail-stock-key")
        assert _get_product_stock(client, "midnight-oud") == 10


# ============================================================
# Cancellation safety
# ============================================================

class TestCancellationSafety:
    def test_double_cancel_does_not_double_restore_stock(
        self, client, admin_token, customer_token, product_a
    ):
        """If two cancel requests race, only one should restore stock.
        With SQLite (tests), this is sequential, but the logic is validated:
        second cancel sees status=cancelled and returns 409."""
        assert _get_product_stock(client, "midnight-oud") == 10

        _add_to_cart(client, customer_token, product_a, quantity=4)
        checkout_resp = _checkout(client, customer_token)
        order_id = checkout_resp.json()["order"]["id"]

        assert _get_product_stock(client, "midnight-oud") == 6

        # First cancel succeeds
        resp1 = client.post(
            f"/api/admin/orders/{order_id}/cancel", headers=_auth(admin_token)
        )
        assert resp1.status_code == 200
        assert _get_product_stock(client, "midnight-oud") == 10

        # Second cancel must fail — stock stays at 10, not 14
        resp2 = client.post(
            f"/api/admin/orders/{order_id}/cancel", headers=_auth(admin_token)
        )
        assert resp2.status_code == 409
        assert _get_product_stock(client, "midnight-oud") == 10


# ============================================================
# Request ID
# ============================================================

class TestRequestID:
    def test_response_contains_request_id_header(self, client):
        resp = client.get("/health")
        assert "X-Request-ID" in resp.headers
        assert len(resp.headers["X-Request-ID"]) > 0

    def test_client_provided_request_id_is_echoed(self, client):
        custom_id = "my-trace-id-12345"
        resp = client.get("/health", headers={"X-Request-ID": custom_id})
        assert resp.headers["X-Request-ID"] == custom_id

    def test_request_id_present_on_api_endpoints(self, client, customer_token, product_a):
        resp = client.get("/api/cart", headers=_auth(customer_token))
        assert "X-Request-ID" in resp.headers

    def test_each_request_gets_unique_id(self, client):
        resp1 = client.get("/health")
        resp2 = client.get("/health")
        assert resp1.headers["X-Request-ID"] != resp2.headers["X-Request-ID"]
