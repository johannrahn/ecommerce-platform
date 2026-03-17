# Architecture

## Modular Monolith

The backend is a **modular monolith** — a single deployable unit where each business domain lives in its own Python package with clear boundaries.

```
app/
├── auth/          # JWT authentication
├── users/         # User profiles
├── catalog/       # Products, categories, images
├── cart/          # Shopping cart
├── orders/        # Checkout, order lifecycle
├── payments/      # Payment provider abstraction
├── promotions/    # Coupons and discount engine
├── reviews/       # Product reviews and ratings
├── notifications/ # User-facing notifications
└── audit/         # Admin audit trail
```

Each module follows the same internal structure:

| File | Responsibility |
|------|---------------|
| `models.py` | SQLAlchemy ORM models |
| `schemas.py` | Pydantic request/response schemas |
| `service.py` | Business logic (validation, queries, transactions) |
| `router.py` | FastAPI route definitions (thin — delegates to service) |

**Why modular monolith over microservices?**
- Single database, single deployment — no distributed transaction complexity
- Module boundaries enforce discipline without network overhead
- Easy to extract into services later if needed
- Appropriate for the scale of a portfolio / small-to-medium e-commerce site

---

## Service Layer Pattern

All business logic lives in `service.py` files. Routers are thin — they parse requests, call services, and return responses.

```python
# router.py — thin
@router.post("/checkout")
def checkout(current_user: CurrentUser, db: DBSession, ...):
    return service.checkout(db, current_user.id, payment_provider)

# service.py — business logic
def checkout(db: Session, user_id: str, payment_provider: PaymentProvider) -> dict:
    # Lock cart, validate stock, calculate totals, process payment, etc.
```

**Why no repository layer?**
- SQLAlchemy already provides a powerful query abstraction
- Adding a repository layer would double the abstraction without clear benefit at this scale
- Services query the ORM directly, keeping the stack pragmatic
- If query complexity grows, repositories can be introduced per-module without changing the service API

---

## Transaction Strategy — Checkout

Checkout is the most critical operation. It follows a strict transaction protocol:

```
1. Lock cart row (SELECT FOR UPDATE)
   └── Prevents double checkout from concurrent requests

2. Validate cart has items

3. Lock product rows in sorted order (SELECT FOR UPDATE)
   └── Sorted by product_id to prevent deadlocks
   └── Same order in every transaction = no circular waits

4. Validate stock for every item

5. Calculate subtotal, validate coupon, compute discount

6. Create Order + OrderItems (prices snapshotted)

7. Decrement stock

8. Process payment
   ├── Success → order=PAID, cart=checked_out, record coupon usage, create notification
   └── Failure → order=FAILED, restore stock, cart stays active, create notification

9. Store idempotency key (if provided)

10. COMMIT (atomic — all or nothing)
```

**Key guarantees:**
- No overselling — stock is locked before validation and decremented atomically
- No double checkout — cart row is locked; second request blocks until first commits
- No deadlocks — product rows always locked in the same sorted order
- No partial state — if anything fails unexpectedly, the entire transaction rolls back
- Safe retries — idempotency key returns the same result without re-processing

---

## Stock Consistency

Stock lives on the `Product` model directly (no separate inventory table in v1).

- Stock is **not** reserved when adding to cart — only validated at checkout
- `SELECT FOR UPDATE` locks the product row during checkout to prevent concurrent modification
- If payment fails, stock is immediately restored within the same transaction
- Admin cancellation also restores stock with the same locking pattern

---

## Coupon Validation Strategy

Coupons are validated at two points:

### At cart apply time (`POST /api/cart/coupon`)
Basic checks only (no subtotal available yet):
- Code exists
- Coupon is active
- Within valid date range
- Usage limit not reached
- One-per-user check

### At checkout time
Full validation including:
- All basic checks (re-validated — coupon may have been deactivated since cart apply)
- `minimum_order_amount` check against actual subtotal

This dual validation ensures:
1. Fast feedback when applying a coupon to the cart
2. Correctness at checkout even if the coupon state changed between apply and checkout

---

## Review Verification

Reviews require purchase verification:

```sql
SELECT 1 FROM order_items
JOIN orders ON orders.id = order_items.order_id
WHERE orders.user_id = :user_id
  AND orders.status = 'paid'
  AND order_items.product_id = :product_id
LIMIT 1
```

- Only users with a **paid** order containing the product can review it
- One review per user per product (enforced by unique constraint)
- Rating aggregation is computed dynamically via `AVG()` / `COUNT()` — no cached columns to get out of sync
- Hidden reviews are excluded from public listing and rating calculation

---

## Notifications

Notifications are created within the same database transaction as the business event:

| Event | Type | Recipient |
|-------|------|-----------|
| Checkout success | `order_paid` | Customer |
| Payment failure | `order_failed` | Customer |
| Admin cancellation | `order_cancelled` | Customer |
| Review hidden | `review_hidden` | Review author |

This ensures notifications are never created for events that didn't actually happen (no race conditions). Users access their notifications via `GET /api/notifications` and can mark them as read individually or in bulk.

---

## Audit Trail

Admin actions that modify sensitive data are logged to the `audit_logs` table:

| Action | Entity Type |
|--------|------------|
| `product.stock_updated` | product |
| `product.active_changed` | product |
| `order.cancelled` | order |
| `review.hidden` | review |
| `review.unhidden` | review |
| `coupon.created` | coupon |
| `coupon.updated` | coupon |
| `coupon.deactivated` | coupon |

Each entry records:
- Who performed the action (`admin_user_id`)
- What changed (`metadata_json` with old/new values)
- When it happened (`created_at`)

Audit logs are written as part of the same transaction as the admin operation — if the operation rolls back, the audit log is also rolled back.

---

## Request Tracing

Every HTTP request gets a unique `X-Request-ID` header:
- Generated by middleware if not provided by the client
- Injected into all log records via a `contextvars.ContextVar`
- Returned in the response headers
- Enables end-to-end request tracing across logs

---

## Authentication

JWT-based authentication with two roles:

- **Customer** — register, login, manage cart, checkout, review products, view notifications
- **Admin** — all customer actions plus: manage catalog, manage coupons, moderate reviews, cancel orders, view audit logs

Tokens are access-only (no refresh tokens in v1). Token expiry defaults to 24 hours.

---

## Testing Strategy

- **205 integration tests** covering all modules
- Tests run against **SQLite in-memory** (no external dependencies)
- Each test gets a fresh database (tables created and dropped per test)
- Tests cover: happy paths, validation errors, access control, edge cases, concurrent scenarios
- Payment provider is injectable — tests can force payment failures via `SimulatedProvider(force_failure=True)`
