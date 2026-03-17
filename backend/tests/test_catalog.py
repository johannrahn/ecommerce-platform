import pytest

from app.auth.security import hash_password
from app.users.models import User, UserRole


@pytest.fixture()
def admin_token(client, db):
    """Create an admin user and return a valid token."""
    user = User(
        email="admin@test.com",
        hashed_password=hash_password("admin123"),
        full_name="Admin",
        role=UserRole.ADMIN,
    )
    db.add(user)
    db.commit()

    resp = client.post(
        "/api/auth/login",
        json={"email": "admin@test.com", "password": "admin123"},
    )
    return resp.json()["access_token"]


@pytest.fixture()
def customer_token(client, db):
    """Create a customer user and return a valid token."""
    client.post(
        "/api/auth/register",
        json={"email": "cust@test.com", "password": "cust123", "full_name": "Customer"},
    )
    resp = client.post(
        "/api/auth/login",
        json={"email": "cust@test.com", "password": "cust123"},
    )
    return resp.json()["access_token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _create_category(client, token, name="Eau de Parfum", slug="eau-de-parfum"):
    return client.post(
        "/api/admin/catalog/categories",
        headers=_auth(token),
        json={"name": name, "slug": slug, "description": "Test category"},
    )


def _create_product(client, token, category_id, name="Test Product", slug="test-product"):
    return client.post(
        "/api/admin/catalog/products",
        headers=_auth(token),
        json={
            "name": name,
            "slug": slug,
            "description": "A test product",
            "price": 99.99,
            "stock": 10,
            "category_id": category_id,
            "images": [{"url": "https://placehold.co/600x800", "is_primary": True}],
        },
    )


# ============================================================
# Category tests
# ============================================================

class TestCategories:
    def test_admin_create_category(self, client, admin_token):
        resp = _create_category(client, admin_token)
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Eau de Parfum"
        assert data["slug"] == "eau-de-parfum"
        assert data["is_active"] is True

    def test_create_category_duplicate_slug(self, client, admin_token):
        _create_category(client, admin_token)
        resp = _create_category(client, admin_token, name="Different", slug="eau-de-parfum")
        assert resp.status_code == 409

    def test_create_category_duplicate_name(self, client, admin_token):
        _create_category(client, admin_token)
        resp = _create_category(client, admin_token, name="Eau de Parfum", slug="different")
        assert resp.status_code == 409

    def test_customer_cannot_create_category(self, client, customer_token):
        resp = client.post(
            "/api/admin/catalog/categories",
            headers=_auth(customer_token),
            json={"name": "Hack", "slug": "hack"},
        )
        assert resp.status_code == 403

    def test_public_list_categories(self, client, admin_token):
        _create_category(client, admin_token)
        _create_category(client, admin_token, name="Cologne", slug="cologne")
        resp = client.get("/api/catalog/categories")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_public_get_category_by_slug(self, client, admin_token):
        _create_category(client, admin_token)
        resp = client.get("/api/catalog/categories/eau-de-parfum")
        assert resp.status_code == 200
        assert resp.json()["slug"] == "eau-de-parfum"

    def test_admin_update_category(self, client, admin_token):
        cat = _create_category(client, admin_token).json()
        resp = client.put(
            f"/api/admin/catalog/categories/{cat['id']}",
            headers=_auth(admin_token),
            json={"description": "Updated"},
        )
        assert resp.status_code == 200
        assert resp.json()["description"] == "Updated"

    def test_admin_delete_category(self, client, admin_token):
        cat = _create_category(client, admin_token).json()
        resp = client.delete(
            f"/api/admin/catalog/categories/{cat['id']}",
            headers=_auth(admin_token),
        )
        assert resp.status_code == 204

    def test_delete_category_with_products_fails(self, client, admin_token):
        cat = _create_category(client, admin_token).json()
        _create_product(client, admin_token, cat["id"])
        resp = client.delete(
            f"/api/admin/catalog/categories/{cat['id']}",
            headers=_auth(admin_token),
        )
        assert resp.status_code == 409

    def test_inactive_categories_hidden_from_public(self, client, admin_token):
        cat = _create_category(client, admin_token).json()
        client.put(
            f"/api/admin/catalog/categories/{cat['id']}",
            headers=_auth(admin_token),
            json={"is_active": False},
        )
        resp = client.get("/api/catalog/categories")
        assert len(resp.json()) == 0

        # Admin still sees it
        resp = client.get("/api/admin/catalog/categories", headers=_auth(admin_token))
        assert len(resp.json()) == 1


# ============================================================
# Product tests
# ============================================================

class TestProducts:
    def test_admin_create_product(self, client, admin_token):
        cat = _create_category(client, admin_token).json()
        resp = _create_product(client, admin_token, cat["id"])
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Test Product"
        assert float(data["price"]) == 99.99
        assert data["stock"] == 10
        assert len(data["images"]) == 1
        assert data["images"][0]["is_primary"] is True
        assert data["category"]["id"] == cat["id"]

    def test_create_product_duplicate_slug(self, client, admin_token):
        cat = _create_category(client, admin_token).json()
        _create_product(client, admin_token, cat["id"])
        resp = _create_product(client, admin_token, cat["id"], name="Other", slug="test-product")
        assert resp.status_code == 409

    def test_create_product_invalid_category(self, client, admin_token):
        resp = _create_product(client, admin_token, "nonexistent-id")
        assert resp.status_code == 404

    def test_public_list_products_paginated(self, client, admin_token):
        cat = _create_category(client, admin_token).json()
        for i in range(5):
            _create_product(client, admin_token, cat["id"], name=f"Prod {i}", slug=f"prod-{i}")

        resp = client.get("/api/catalog/products?per_page=2&page=1")
        data = resp.json()
        assert resp.status_code == 200
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["pages"] == 3
        assert data["page"] == 1

    def test_public_filter_by_category(self, client, admin_token):
        cat1 = _create_category(client, admin_token).json()
        cat2 = _create_category(client, admin_token, name="Cologne", slug="cologne").json()
        _create_product(client, admin_token, cat1["id"], name="P1", slug="p1")
        _create_product(client, admin_token, cat2["id"], name="P2", slug="p2")

        resp = client.get(f"/api/catalog/products?category_id={cat1['id']}")
        assert len(resp.json()["items"]) == 1
        assert resp.json()["items"][0]["name"] == "P1"

    def test_public_search_by_name(self, client, admin_token):
        cat = _create_category(client, admin_token).json()
        _create_product(client, admin_token, cat["id"], name="Midnight Oud", slug="midnight-oud")
        _create_product(client, admin_token, cat["id"], name="Velvet Rose", slug="velvet-rose")

        resp = client.get("/api/catalog/products?search=midnight")
        assert len(resp.json()["items"]) == 1
        assert resp.json()["items"][0]["name"] == "Midnight Oud"

    def test_public_get_product_by_slug(self, client, admin_token):
        cat = _create_category(client, admin_token).json()
        _create_product(client, admin_token, cat["id"])
        resp = client.get("/api/catalog/products/test-product")
        assert resp.status_code == 200
        assert resp.json()["slug"] == "test-product"

    def test_admin_update_product(self, client, admin_token):
        cat = _create_category(client, admin_token).json()
        prod = _create_product(client, admin_token, cat["id"]).json()
        resp = client.put(
            f"/api/admin/catalog/products/{prod['id']}",
            headers=_auth(admin_token),
            json={"price": 149.99},
        )
        assert resp.status_code == 200
        assert float(resp.json()["price"]) == 149.99

    def test_admin_delete_product(self, client, admin_token):
        cat = _create_category(client, admin_token).json()
        prod = _create_product(client, admin_token, cat["id"]).json()
        resp = client.delete(
            f"/api/admin/catalog/products/{prod['id']}",
            headers=_auth(admin_token),
        )
        assert resp.status_code == 204

        # Verify deleted
        resp = client.get("/api/catalog/products/test-product")
        assert resp.status_code == 404

    def test_inactive_products_hidden_from_public(self, client, admin_token):
        cat = _create_category(client, admin_token).json()
        prod = _create_product(client, admin_token, cat["id"]).json()
        client.put(
            f"/api/admin/catalog/products/{prod['id']}",
            headers=_auth(admin_token),
            json={"is_active": False},
        )
        resp = client.get("/api/catalog/products")
        assert len(resp.json()["items"]) == 0

    def test_primary_image_in_list(self, client, admin_token):
        cat = _create_category(client, admin_token).json()
        _create_product(client, admin_token, cat["id"])
        resp = client.get("/api/catalog/products")
        item = resp.json()["items"][0]
        assert item["primary_image"] == "https://placehold.co/600x800"


# ============================================================
# Product image tests
# ============================================================

class TestProductImages:
    def test_add_image_to_product(self, client, admin_token):
        cat = _create_category(client, admin_token).json()
        prod = _create_product(client, admin_token, cat["id"]).json()
        resp = client.post(
            f"/api/admin/catalog/products/{prod['id']}/images",
            headers=_auth(admin_token),
            json={"url": "https://placehold.co/800x800", "is_primary": False, "sort_order": 1},
        )
        assert resp.status_code == 201
        assert len(resp.json()["images"]) == 2

    def test_delete_image(self, client, admin_token):
        cat = _create_category(client, admin_token).json()
        prod = _create_product(client, admin_token, cat["id"]).json()
        image_id = prod["images"][0]["id"]
        resp = client.delete(
            f"/api/admin/catalog/images/{image_id}",
            headers=_auth(admin_token),
        )
        assert resp.status_code == 204
