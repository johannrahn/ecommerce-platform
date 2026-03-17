import pytest

from app.auth.security import hash_password
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
        json={"email": "cust@test.com", "password": "cust123", "full_name": "Customer One"},
    )
    resp = client.post("/api/auth/login", json={"email": "cust@test.com", "password": "cust123"})
    return resp.json()["access_token"]


@pytest.fixture()
def customer2_token(client):
    client.post(
        "/api/auth/register",
        json={"email": "cust2@test.com", "password": "cust2123", "full_name": "Customer Two"},
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


def _checkout(client, token):
    return client.post("/api/orders/checkout", headers=_auth(token))


def _buy_product(client, token, product_id, quantity=1):
    """Helper: add to cart and checkout, return order."""
    _add_to_cart(client, token, product_id, quantity)
    return _checkout(client, token)


def _create_review(client, token, slug, rating=5, title=None, comment=None):
    data = {"rating": rating}
    if title:
        data["title"] = title
    if comment:
        data["comment"] = comment
    return client.post(
        f"/api/products/{slug}/reviews",
        headers=_auth(token),
        json=data,
    )


# ============================================================
# Create Review
# ============================================================

class TestCreateReview:
    def test_purchaser_can_create_review(self, client, admin_token, customer_token, product_a):
        _buy_product(client, customer_token, product_a)

        resp = _create_review(client, customer_token, "midnight-oud", rating=4, title="Great", comment="Love it")
        assert resp.status_code == 201
        data = resp.json()
        assert data["rating"] == 4
        assert data["title"] == "Great"
        assert data["comment"] == "Love it"
        assert data["is_visible"] is True
        assert data["user_name"] == "Customer One"

    def test_non_purchaser_cannot_review(self, client, admin_token, customer_token, product_a):
        # Don't buy, just try to review
        resp = _create_review(client, customer_token, "midnight-oud", rating=5)
        assert resp.status_code == 403
        assert "purchased" in resp.json()["detail"].lower()

    def test_duplicate_review_rejected(self, client, admin_token, customer_token, product_a):
        _buy_product(client, customer_token, product_a)
        resp1 = _create_review(client, customer_token, "midnight-oud", rating=5)
        assert resp1.status_code == 201

        resp2 = _create_review(client, customer_token, "midnight-oud", rating=3)
        assert resp2.status_code == 409
        assert "already reviewed" in resp2.json()["detail"].lower()

    def test_invalid_rating_rejected(self, client, admin_token, customer_token, product_a):
        _buy_product(client, customer_token, product_a)
        resp = client.post(
            "/api/products/midnight-oud/reviews",
            headers=_auth(customer_token),
            json={"rating": 0},
        )
        assert resp.status_code == 422

        resp = client.post(
            "/api/products/midnight-oud/reviews",
            headers=_auth(customer_token),
            json={"rating": 6},
        )
        assert resp.status_code == 422

    def test_unauthenticated_cannot_review(self, client, admin_token, product_a):
        resp = client.post(
            "/api/products/midnight-oud/reviews",
            json={"rating": 5},
        )
        assert resp.status_code == 401

    def test_review_nonexistent_product(self, client, customer_token):
        resp = _create_review(client, customer_token, "nonexistent-slug", rating=5)
        assert resp.status_code == 404

    def test_review_with_only_rating(self, client, admin_token, customer_token, product_a):
        _buy_product(client, customer_token, product_a)
        resp = _create_review(client, customer_token, "midnight-oud", rating=3)
        assert resp.status_code == 201
        assert resp.json()["title"] is None
        assert resp.json()["comment"] is None


# ============================================================
# Edit Review
# ============================================================

class TestEditReview:
    def test_user_can_edit_own_review(self, client, admin_token, customer_token, product_a):
        _buy_product(client, customer_token, product_a)
        create_resp = _create_review(client, customer_token, "midnight-oud", rating=3)
        review_id = create_resp.json()["id"]

        resp = client.put(
            f"/api/reviews/{review_id}",
            headers=_auth(customer_token),
            json={"rating": 5, "title": "Updated"},
        )
        assert resp.status_code == 200
        assert resp.json()["rating"] == 5
        assert resp.json()["title"] == "Updated"

    def test_user_cannot_edit_another_users_review(
        self, client, admin_token, customer_token, customer2_token, product_a
    ):
        _buy_product(client, customer_token, product_a)
        create_resp = _create_review(client, customer_token, "midnight-oud", rating=4)
        review_id = create_resp.json()["id"]

        # Customer 2 tries to edit Customer 1's review
        resp = client.put(
            f"/api/reviews/{review_id}",
            headers=_auth(customer2_token),
            json={"rating": 1},
        )
        assert resp.status_code == 403

    def test_edit_nonexistent_review(self, client, customer_token):
        resp = client.put(
            "/api/reviews/fake-id",
            headers=_auth(customer_token),
            json={"rating": 5},
        )
        assert resp.status_code == 404


# ============================================================
# Delete Review
# ============================================================

class TestDeleteReview:
    def test_user_can_delete_own_review(self, client, admin_token, customer_token, product_a):
        _buy_product(client, customer_token, product_a)
        create_resp = _create_review(client, customer_token, "midnight-oud", rating=5)
        review_id = create_resp.json()["id"]

        resp = client.delete(f"/api/reviews/{review_id}", headers=_auth(customer_token))
        assert resp.status_code == 204

        # Verify it's gone
        reviews = client.get("/api/products/midnight-oud/reviews")
        assert len(reviews.json()) == 0

    def test_user_cannot_delete_another_users_review(
        self, client, admin_token, customer_token, customer2_token, product_a
    ):
        _buy_product(client, customer_token, product_a)
        create_resp = _create_review(client, customer_token, "midnight-oud", rating=4)
        review_id = create_resp.json()["id"]

        resp = client.delete(f"/api/reviews/{review_id}", headers=_auth(customer2_token))
        assert resp.status_code == 403


# ============================================================
# Admin Moderation (Hide / Unhide)
# ============================================================

class TestAdminModeration:
    def test_admin_can_hide_review(self, client, admin_token, customer_token, product_a):
        _buy_product(client, customer_token, product_a)
        create_resp = _create_review(client, customer_token, "midnight-oud", rating=5)
        review_id = create_resp.json()["id"]

        resp = client.post(f"/api/admin/reviews/{review_id}/hide", headers=_auth(admin_token))
        assert resp.status_code == 200
        assert resp.json()["is_visible"] is False

    def test_admin_can_unhide_review(self, client, admin_token, customer_token, product_a):
        _buy_product(client, customer_token, product_a)
        create_resp = _create_review(client, customer_token, "midnight-oud", rating=5)
        review_id = create_resp.json()["id"]

        client.post(f"/api/admin/reviews/{review_id}/hide", headers=_auth(admin_token))
        resp = client.post(f"/api/admin/reviews/{review_id}/unhide", headers=_auth(admin_token))
        assert resp.status_code == 200
        assert resp.json()["is_visible"] is True

    def test_hidden_review_not_shown_publicly(self, client, admin_token, customer_token, product_a):
        _buy_product(client, customer_token, product_a)
        _create_review(client, customer_token, "midnight-oud", rating=5)

        # Before hiding
        reviews = client.get("/api/products/midnight-oud/reviews").json()
        assert len(reviews) == 1

        review_id = reviews[0]["id"]
        client.post(f"/api/admin/reviews/{review_id}/hide", headers=_auth(admin_token))

        # After hiding — public listing should be empty
        reviews = client.get("/api/products/midnight-oud/reviews").json()
        assert len(reviews) == 0

    def test_customer_cannot_hide_review(self, client, admin_token, customer_token, product_a):
        _buy_product(client, customer_token, product_a)
        create_resp = _create_review(client, customer_token, "midnight-oud", rating=5)
        review_id = create_resp.json()["id"]

        resp = client.post(f"/api/admin/reviews/{review_id}/hide", headers=_auth(customer_token))
        assert resp.status_code == 403

    def test_hide_nonexistent_review(self, client, admin_token):
        resp = client.post("/api/admin/reviews/fake-id/hide", headers=_auth(admin_token))
        assert resp.status_code == 404


# ============================================================
# Product Rating Aggregation
# ============================================================

class TestRatingAggregation:
    def test_average_rating_and_count(
        self, client, admin_token, customer_token, customer2_token, product_a
    ):
        _buy_product(client, customer_token, product_a)
        _buy_product(client, customer2_token, product_a)

        _create_review(client, customer_token, "midnight-oud", rating=4)
        _create_review(client, customer2_token, "midnight-oud", rating=2)

        resp = client.get("/api/catalog/products/midnight-oud")
        data = resp.json()
        assert data["average_rating"] == 3.0
        assert data["reviews_count"] == 2

    def test_no_reviews_returns_null_average(self, client, admin_token, product_a):
        resp = client.get("/api/catalog/products/midnight-oud")
        data = resp.json()
        assert data["average_rating"] is None
        assert data["reviews_count"] == 0

    def test_hidden_review_excluded_from_aggregation(
        self, client, admin_token, customer_token, customer2_token, product_a
    ):
        _buy_product(client, customer_token, product_a)
        _buy_product(client, customer2_token, product_a)

        _create_review(client, customer_token, "midnight-oud", rating=5)
        resp2 = _create_review(client, customer2_token, "midnight-oud", rating=1)
        review_id = resp2.json()["id"]

        # Hide the 1-star review
        client.post(f"/api/admin/reviews/{review_id}/hide", headers=_auth(admin_token))

        resp = client.get("/api/catalog/products/midnight-oud")
        data = resp.json()
        assert data["average_rating"] == 5.0
        assert data["reviews_count"] == 1

    def test_product_list_includes_rating_aggregates(
        self, client, admin_token, customer_token, product_a, product_b
    ):
        _buy_product(client, customer_token, product_a)
        _create_review(client, customer_token, "midnight-oud", rating=4)

        resp = client.get("/api/catalog/products")
        products = resp.json()["items"]
        # Find midnight-oud in the list
        oud = next(p for p in products if p["slug"] == "midnight-oud")
        breeze = next(p for p in products if p["slug"] == "citrus-breeze")

        assert oud["average_rating"] == 4.0
        assert oud["reviews_count"] == 1
        assert breeze["average_rating"] is None
        assert breeze["reviews_count"] == 0


# ============================================================
# List Product Reviews
# ============================================================

class TestListReviews:
    def test_list_reviews_for_product(self, client, admin_token, customer_token, product_a):
        _buy_product(client, customer_token, product_a)
        _create_review(client, customer_token, "midnight-oud", rating=5, title="Amazing")

        resp = client.get("/api/products/midnight-oud/reviews")
        assert resp.status_code == 200
        reviews = resp.json()
        assert len(reviews) == 1
        assert reviews[0]["rating"] == 5
        assert reviews[0]["title"] == "Amazing"

    def test_list_reviews_empty(self, client, admin_token, product_a):
        resp = client.get("/api/products/midnight-oud/reviews")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_reviews_unauthenticated(self, client, admin_token, product_a):
        """Public endpoint — no auth required."""
        resp = client.get("/api/products/midnight-oud/reviews")
        assert resp.status_code == 200
