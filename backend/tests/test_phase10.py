import json

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
    _add_to_cart(client, token, product_id, quantity)
    return _checkout(client, token)


# ============================================================
# Notifications — Checkout Events
# ============================================================

class TestCheckoutNotifications:
    def test_notification_on_successful_checkout(
        self, client, admin_token, customer_token, product_a
    ):
        _buy_product(client, customer_token, product_a)

        resp = client.get("/api/notifications", headers=_auth(customer_token))
        assert resp.status_code == 200
        notifications = resp.json()
        assert len(notifications) == 1
        assert notifications[0]["type"] == "order_paid"
        assert "confirmed" in notifications[0]["title"].lower()
        assert notifications[0]["is_read"] is False

    def test_notification_on_failed_payment(
        self, client, admin_token, customer_token, product_a
    ):
        failing = SimulatedProvider(force_failure=True)
        app.dependency_overrides[get_payment_provider] = lambda: failing

        _add_to_cart(client, customer_token, product_a, quantity=1)
        _checkout(client, customer_token)

        app.dependency_overrides.pop(get_payment_provider, None)

        resp = client.get("/api/notifications", headers=_auth(customer_token))
        notifications = resp.json()
        assert len(notifications) == 1
        assert notifications[0]["type"] == "order_failed"
        assert "failed" in notifications[0]["title"].lower()

    def test_notification_on_admin_order_cancellation(
        self, client, admin_token, customer_token, product_a
    ):
        checkout_resp = _buy_product(client, customer_token, product_a)
        order_id = checkout_resp.json()["order"]["id"]

        client.post(
            f"/api/admin/orders/{order_id}/cancel",
            headers=_auth(admin_token),
        )

        resp = client.get("/api/notifications", headers=_auth(customer_token))
        notifications = resp.json()
        types = [n["type"] for n in notifications]
        assert "order_cancelled" in types
        assert "order_paid" in types


# ============================================================
# Notifications — Review Moderation
# ============================================================

class TestReviewNotifications:
    def test_notification_on_review_hidden(
        self, client, admin_token, customer_token, product_a
    ):
        _buy_product(client, customer_token, product_a)
        review_resp = client.post(
            "/api/products/midnight-oud/reviews",
            headers=_auth(customer_token),
            json={"rating": 5, "title": "Great"},
        )
        review_id = review_resp.json()["id"]

        client.post(
            f"/api/admin/reviews/{review_id}/hide",
            headers=_auth(admin_token),
        )

        resp = client.get("/api/notifications", headers=_auth(customer_token))
        notifications = resp.json()
        types = [n["type"] for n in notifications]
        assert "review_hidden" in types


# ============================================================
# Notifications — User Access Control
# ============================================================

class TestNotificationAccess:
    def test_user_only_sees_own_notifications(
        self, client, admin_token, customer_token, customer2_token, product_a
    ):
        _buy_product(client, customer_token, product_a)
        _buy_product(client, customer2_token, product_a)

        resp1 = client.get("/api/notifications", headers=_auth(customer_token))
        resp2 = client.get("/api/notifications", headers=_auth(customer2_token))
        assert len(resp1.json()) == 1
        assert len(resp2.json()) == 1
        # Different notification IDs
        assert resp1.json()[0]["id"] != resp2.json()[0]["id"]

    def test_unauthenticated_cannot_access_notifications(self, client):
        resp = client.get("/api/notifications")
        assert resp.status_code == 401


# ============================================================
# Notifications — Mark Read
# ============================================================

class TestNotificationRead:
    def test_mark_single_notification_as_read(
        self, client, admin_token, customer_token, product_a
    ):
        _buy_product(client, customer_token, product_a)
        notifications = client.get(
            "/api/notifications", headers=_auth(customer_token)
        ).json()
        notif_id = notifications[0]["id"]

        resp = client.post(
            f"/api/notifications/{notif_id}/read",
            headers=_auth(customer_token),
        )
        assert resp.status_code == 200
        assert resp.json()["is_read"] is True

    def test_mark_all_notifications_as_read(
        self, client, admin_token, customer_token, product_a
    ):
        # Create two notifications (buy + cancel)
        checkout_resp = _buy_product(client, customer_token, product_a)
        order_id = checkout_resp.json()["order"]["id"]
        client.post(
            f"/api/admin/orders/{order_id}/cancel",
            headers=_auth(admin_token),
        )

        resp = client.post(
            "/api/notifications/read-all",
            headers=_auth(customer_token),
        )
        assert resp.status_code == 200
        assert resp.json()["marked_read"] == 2

        # Verify all are read
        notifications = client.get(
            "/api/notifications", headers=_auth(customer_token)
        ).json()
        assert all(n["is_read"] for n in notifications)

    def test_mark_nonexistent_notification_returns_404(
        self, client, customer_token
    ):
        resp = client.post(
            "/api/notifications/fake-id/read",
            headers=_auth(customer_token),
        )
        assert resp.status_code == 404

    def test_cannot_mark_other_users_notification(
        self, client, admin_token, customer_token, customer2_token, product_a
    ):
        _buy_product(client, customer_token, product_a)
        notifications = client.get(
            "/api/notifications", headers=_auth(customer_token)
        ).json()
        notif_id = notifications[0]["id"]

        # Customer 2 tries to read customer 1's notification
        resp = client.post(
            f"/api/notifications/{notif_id}/read",
            headers=_auth(customer2_token),
        )
        assert resp.status_code == 404


# ============================================================
# Audit Logs — Admin Actions
# ============================================================

class TestAuditLogCreation:
    def test_audit_log_on_stock_update(self, client, admin_token, product_a):
        client.put(
            f"/api/admin/catalog/products/{product_a}",
            headers=_auth(admin_token),
            json={"stock": 50},
        )

        resp = client.get("/api/admin/audit-logs", headers=_auth(admin_token))
        assert resp.status_code == 200
        logs = resp.json()["items"]
        stock_logs = [l for l in logs if l["action"] == "product.stock_updated"]
        assert len(stock_logs) == 1
        meta = json.loads(stock_logs[0]["metadata_json"])
        assert meta["old_stock"] == 10
        assert meta["new_stock"] == 50

    def test_audit_log_on_product_deactivation(self, client, admin_token, product_a):
        client.put(
            f"/api/admin/catalog/products/{product_a}",
            headers=_auth(admin_token),
            json={"is_active": False},
        )

        resp = client.get("/api/admin/audit-logs", headers=_auth(admin_token))
        logs = resp.json()["items"]
        active_logs = [l for l in logs if l["action"] == "product.active_changed"]
        assert len(active_logs) == 1

    def test_audit_log_on_admin_order_cancellation(
        self, client, admin_token, customer_token, product_a
    ):
        checkout_resp = _buy_product(client, customer_token, product_a)
        order_id = checkout_resp.json()["order"]["id"]

        client.post(
            f"/api/admin/orders/{order_id}/cancel",
            headers=_auth(admin_token),
        )

        resp = client.get("/api/admin/audit-logs", headers=_auth(admin_token))
        logs = resp.json()["items"]
        cancel_logs = [l for l in logs if l["action"] == "order.cancelled"]
        assert len(cancel_logs) == 1
        assert cancel_logs[0]["entity_type"] == "order"
        assert cancel_logs[0]["entity_id"] == order_id

    def test_audit_log_on_review_hide(
        self, client, admin_token, customer_token, product_a
    ):
        _buy_product(client, customer_token, product_a)
        review_resp = client.post(
            "/api/products/midnight-oud/reviews",
            headers=_auth(customer_token),
            json={"rating": 4},
        )
        review_id = review_resp.json()["id"]

        client.post(
            f"/api/admin/reviews/{review_id}/hide",
            headers=_auth(admin_token),
        )

        resp = client.get("/api/admin/audit-logs", headers=_auth(admin_token))
        logs = resp.json()["items"]
        hide_logs = [l for l in logs if l["action"] == "review.hidden"]
        assert len(hide_logs) == 1
        assert hide_logs[0]["entity_id"] == review_id

    def test_audit_log_on_review_unhide(
        self, client, admin_token, customer_token, product_a
    ):
        _buy_product(client, customer_token, product_a)
        review_resp = client.post(
            "/api/products/midnight-oud/reviews",
            headers=_auth(customer_token),
            json={"rating": 4},
        )
        review_id = review_resp.json()["id"]

        client.post(
            f"/api/admin/reviews/{review_id}/hide",
            headers=_auth(admin_token),
        )
        client.post(
            f"/api/admin/reviews/{review_id}/unhide",
            headers=_auth(admin_token),
        )

        resp = client.get("/api/admin/audit-logs", headers=_auth(admin_token))
        logs = resp.json()["items"]
        actions = [l["action"] for l in logs]
        assert "review.hidden" in actions
        assert "review.unhidden" in actions

    def test_audit_log_on_coupon_create(self, client, admin_token):
        client.post(
            "/api/admin/coupons",
            headers=_auth(admin_token),
            json={"code": "SAVE10", "discount_type": "percent", "discount_value": 10},
        )

        resp = client.get("/api/admin/audit-logs", headers=_auth(admin_token))
        logs = resp.json()["items"]
        create_logs = [l for l in logs if l["action"] == "coupon.created"]
        assert len(create_logs) == 1

    def test_audit_log_on_coupon_update(self, client, admin_token):
        create_resp = client.post(
            "/api/admin/coupons",
            headers=_auth(admin_token),
            json={"code": "UPD", "discount_type": "fixed", "discount_value": 5},
        )
        coupon_id = create_resp.json()["id"]

        client.put(
            f"/api/admin/coupons/{coupon_id}",
            headers=_auth(admin_token),
            json={"discount_value": 15},
        )

        resp = client.get("/api/admin/audit-logs", headers=_auth(admin_token))
        logs = resp.json()["items"]
        update_logs = [l for l in logs if l["action"] == "coupon.updated"]
        assert len(update_logs) == 1

    def test_audit_log_on_coupon_deactivate(self, client, admin_token):
        create_resp = client.post(
            "/api/admin/coupons",
            headers=_auth(admin_token),
            json={"code": "DEACT", "discount_type": "fixed", "discount_value": 5},
        )
        coupon_id = create_resp.json()["id"]

        client.put(
            f"/api/admin/coupons/{coupon_id}",
            headers=_auth(admin_token),
            json={"is_active": False},
        )

        resp = client.get("/api/admin/audit-logs", headers=_auth(admin_token))
        logs = resp.json()["items"]
        deact_logs = [l for l in logs if l["action"] == "coupon.deactivated"]
        assert len(deact_logs) == 1


# ============================================================
# Audit Logs — Access Control
# ============================================================

class TestAuditLogAccess:
    def test_non_admin_cannot_access_audit_logs(self, client, customer_token):
        resp = client.get("/api/admin/audit-logs", headers=_auth(customer_token))
        assert resp.status_code == 403

    def test_unauthenticated_cannot_access_audit_logs(self, client):
        resp = client.get("/api/admin/audit-logs")
        assert resp.status_code == 401


# ============================================================
# Audit Logs — Filtering & Pagination
# ============================================================

class TestAuditLogFiltering:
    def test_filter_by_action(self, client, admin_token, product_a):
        # Create two types of audit logs
        client.put(
            f"/api/admin/catalog/products/{product_a}",
            headers=_auth(admin_token),
            json={"stock": 50},
        )
        client.put(
            f"/api/admin/catalog/products/{product_a}",
            headers=_auth(admin_token),
            json={"is_active": False},
        )

        resp = client.get(
            "/api/admin/audit-logs?action=product.stock_updated",
            headers=_auth(admin_token),
        )
        logs = resp.json()
        assert logs["total"] == 1
        assert logs["items"][0]["action"] == "product.stock_updated"

    def test_filter_by_entity_type(self, client, admin_token, product_a):
        # Create product audit log
        client.put(
            f"/api/admin/catalog/products/{product_a}",
            headers=_auth(admin_token),
            json={"stock": 50},
        )
        # Create coupon audit log
        client.post(
            "/api/admin/coupons",
            headers=_auth(admin_token),
            json={"code": "X1", "discount_type": "fixed", "discount_value": 5},
        )

        resp = client.get(
            "/api/admin/audit-logs?entity_type=product",
            headers=_auth(admin_token),
        )
        logs = resp.json()
        assert logs["total"] == 1
        assert all(l["entity_type"] == "product" for l in logs["items"])

    def test_pagination(self, client, admin_token, product_a):
        # Create several audit logs
        for i in range(5):
            client.put(
                f"/api/admin/catalog/products/{product_a}",
                headers=_auth(admin_token),
                json={"stock": 20 + i},
            )

        resp = client.get(
            "/api/admin/audit-logs?limit=2&offset=0",
            headers=_auth(admin_token),
        )
        logs = resp.json()
        assert logs["total"] == 5
        assert len(logs["items"]) == 2
        assert logs["limit"] == 2
        assert logs["offset"] == 0

        resp2 = client.get(
            "/api/admin/audit-logs?limit=2&offset=2",
            headers=_auth(admin_token),
        )
        logs2 = resp2.json()
        assert logs2["total"] == 5
        assert len(logs2["items"]) == 2
        assert logs2["offset"] == 2
        # Different items
        assert logs["items"][0]["id"] != logs2["items"][0]["id"]

    def test_empty_audit_log(self, client, admin_token):
        resp = client.get("/api/admin/audit-logs", headers=_auth(admin_token))
        assert resp.status_code == 200
        assert resp.json()["total"] == 0
        assert resp.json()["items"] == []
