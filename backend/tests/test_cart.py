import pytest

from app.auth.security import hash_password
from app.users.models import User, UserRole


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


@pytest.fixture()
def product_id(client, admin_token, category_id):
    resp = client.post(
        "/api/admin/catalog/products",
        headers=_auth(admin_token),
        json={
            "name": "Midnight Oud",
            "slug": "midnight-oud",
            "price": 99.99,
            "stock": 10,
            "category_id": category_id,
            "images": [{"url": "https://placehold.co/600x800", "is_primary": True}],
        },
    )
    return resp.json()["id"]


@pytest.fixture()
def product_id_2(client, admin_token, category_id):
    resp = client.post(
        "/api/admin/catalog/products",
        headers=_auth(admin_token),
        json={
            "name": "Velvet Rose",
            "slug": "velvet-rose",
            "price": 149.99,
            "stock": 5,
            "category_id": category_id,
        },
    )
    return resp.json()["id"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


class TestCartBasics:
    def test_get_empty_cart(self, client, customer_token):
        resp = client.get("/api/cart", headers=_auth(customer_token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["items"] == []
        assert data["item_count"] == 0
        assert data["total"] == 0.0

    def test_unauthenticated_cannot_access_cart(self, client):
        resp = client.get("/api/cart")
        assert resp.status_code == 401


class TestAddItem:
    def test_add_item_to_cart(self, client, customer_token, product_id):
        resp = client.post(
            "/api/cart/items",
            headers=_auth(customer_token),
            json={"product_id": product_id, "quantity": 2},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["item_count"] == 1
        assert data["items"][0]["quantity"] == 2
        assert data["items"][0]["product_name"] == "Midnight Oud"
        assert float(data["items"][0]["subtotal"]) == 199.98
        assert float(data["total"]) == 199.98

    def test_add_same_product_increments_quantity(self, client, customer_token, product_id):
        client.post(
            "/api/cart/items",
            headers=_auth(customer_token),
            json={"product_id": product_id, "quantity": 2},
        )
        resp = client.post(
            "/api/cart/items",
            headers=_auth(customer_token),
            json={"product_id": product_id, "quantity": 3},
        )
        data = resp.json()
        assert data["item_count"] == 1
        assert data["items"][0]["quantity"] == 5

    def test_add_multiple_products(self, client, customer_token, product_id, product_id_2):
        client.post(
            "/api/cart/items",
            headers=_auth(customer_token),
            json={"product_id": product_id, "quantity": 1},
        )
        resp = client.post(
            "/api/cart/items",
            headers=_auth(customer_token),
            json={"product_id": product_id_2, "quantity": 2},
        )
        data = resp.json()
        assert data["item_count"] == 2
        assert float(data["total"]) == 99.99 + (149.99 * 2)

    def test_add_nonexistent_product_fails(self, client, customer_token):
        resp = client.post(
            "/api/cart/items",
            headers=_auth(customer_token),
            json={"product_id": "nonexistent", "quantity": 1},
        )
        assert resp.status_code == 404

    def test_add_inactive_product_fails(self, client, customer_token, admin_token, product_id):
        client.put(
            f"/api/admin/catalog/products/{product_id}",
            headers=_auth(admin_token),
            json={"is_active": False},
        )
        resp = client.post(
            "/api/cart/items",
            headers=_auth(customer_token),
            json={"product_id": product_id, "quantity": 1},
        )
        assert resp.status_code == 404

    def test_add_zero_quantity_fails(self, client, customer_token, product_id):
        resp = client.post(
            "/api/cart/items",
            headers=_auth(customer_token),
            json={"product_id": product_id, "quantity": 0},
        )
        assert resp.status_code == 422

    def test_primary_image_included(self, client, customer_token, product_id):
        resp = client.post(
            "/api/cart/items",
            headers=_auth(customer_token),
            json={"product_id": product_id, "quantity": 1},
        )
        assert resp.json()["items"][0]["primary_image"] == "https://placehold.co/600x800"

    def test_no_image_returns_null(self, client, customer_token, product_id_2):
        resp = client.post(
            "/api/cart/items",
            headers=_auth(customer_token),
            json={"product_id": product_id_2, "quantity": 1},
        )
        assert resp.json()["items"][0]["primary_image"] is None


class TestUpdateItem:
    def test_update_quantity(self, client, customer_token, product_id):
        resp = client.post(
            "/api/cart/items",
            headers=_auth(customer_token),
            json={"product_id": product_id, "quantity": 1},
        )
        item_id = resp.json()["items"][0]["id"]

        resp = client.put(
            f"/api/cart/items/{item_id}",
            headers=_auth(customer_token),
            json={"quantity": 5},
        )
        assert resp.status_code == 200
        assert resp.json()["items"][0]["quantity"] == 5

    def test_update_nonexistent_item_fails(self, client, customer_token):
        resp = client.put(
            "/api/cart/items/nonexistent",
            headers=_auth(customer_token),
            json={"quantity": 5},
        )
        assert resp.status_code == 404


class TestRemoveItem:
    def test_remove_item(self, client, customer_token, product_id):
        resp = client.post(
            "/api/cart/items",
            headers=_auth(customer_token),
            json={"product_id": product_id, "quantity": 1},
        )
        item_id = resp.json()["items"][0]["id"]

        resp = client.delete(
            f"/api/cart/items/{item_id}", headers=_auth(customer_token)
        )
        assert resp.status_code == 200
        assert resp.json()["item_count"] == 0

    def test_remove_nonexistent_item_fails(self, client, customer_token):
        resp = client.delete(
            "/api/cart/items/nonexistent", headers=_auth(customer_token)
        )
        assert resp.status_code == 404


class TestClearCart:
    def test_clear_cart(self, client, customer_token, product_id, product_id_2):
        client.post(
            "/api/cart/items",
            headers=_auth(customer_token),
            json={"product_id": product_id, "quantity": 2},
        )
        client.post(
            "/api/cart/items",
            headers=_auth(customer_token),
            json={"product_id": product_id_2, "quantity": 1},
        )

        resp = client.delete("/api/cart", headers=_auth(customer_token))
        assert resp.status_code == 200
        assert resp.json()["item_count"] == 0
        assert resp.json()["total"] == 0.0


class TestCartIsolation:
    def test_carts_are_per_user(self, client, customer_token, product_id, db):
        # Customer adds to cart
        client.post(
            "/api/cart/items",
            headers=_auth(customer_token),
            json={"product_id": product_id, "quantity": 3},
        )

        # Second customer
        client.post(
            "/api/auth/register",
            json={"email": "other@test.com", "password": "pass123", "full_name": "Other"},
        )
        other_login = client.post(
            "/api/auth/login",
            json={"email": "other@test.com", "password": "pass123"},
        )
        other_token = other_login.json()["access_token"]

        resp = client.get("/api/cart", headers=_auth(other_token))
        assert resp.json()["item_count"] == 0
