# API Overview

Base URL: `http://localhost:8000/api`

Interactive docs: `http://localhost:8000/docs` (Swagger UI) | `http://localhost:8000/redoc` (ReDoc)

---

## Authentication

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/register` | - | Create a new account |
| POST | `/auth/login` | - | Get JWT access token |

**Register:**
```json
POST /api/auth/register
{ "email": "user@example.com", "password": "secret123", "full_name": "Jane Doe" }
```

**Login:**
```json
POST /api/auth/login
{ "email": "user@example.com", "password": "secret123" }

→ { "access_token": "eyJ...", "token_type": "bearer" }
```

All authenticated endpoints require: `Authorization: Bearer <token>`

---

## Catalog (Public)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/catalog/categories` | - | List active categories |
| GET | `/catalog/categories/{slug}` | - | Get category by slug |
| GET | `/catalog/products` | - | List products (paginated) |
| GET | `/catalog/products/{slug}` | - | Get product detail |

**List products with search:**
```
GET /api/catalog/products?page=1&per_page=10&search=oud&category_id=abc
```

Product responses include `average_rating` and `reviews_count`.

---

## Cart

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/cart` | User | Get my cart |
| POST | `/cart/items` | User | Add item to cart |
| PUT | `/cart/items/{item_id}` | User | Update item quantity |
| DELETE | `/cart/items/{item_id}` | User | Remove item from cart |
| POST | `/cart/coupon` | User | Apply coupon to cart |
| DELETE | `/cart/coupon` | User | Remove coupon from cart |
| DELETE | `/cart` | User | Clear cart |

**Add to cart:**
```json
POST /api/cart/items
{ "product_id": "abc-123", "quantity": 2 }
```

**Apply coupon:**
```json
POST /api/cart/coupon
{ "code": "SAVE10" }
```

---

## Orders

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/orders/checkout` | User | Checkout cart |
| GET | `/orders` | User | List my orders |
| GET | `/orders/{order_id}` | User | Get order detail |

**Checkout:**
```
POST /api/orders/checkout
Header: Idempotency-Key: unique-key-123 (optional)
```

Response includes `subtotal`, `discount_amount`, `total`, `coupon_code`, and `payment_message`.

---

## Reviews

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/products/{slug}/reviews` | User | Create review (must have purchased) |
| GET | `/products/{slug}/reviews` | - | List product reviews |
| PUT | `/reviews/{review_id}` | User | Edit own review |
| DELETE | `/reviews/{review_id}` | User | Delete own review |

**Create review:**
```json
POST /api/products/midnight-oud/reviews
{ "rating": 5, "title": "Amazing scent", "comment": "Rich and long-lasting." }
```

Rating must be 1-5. Title and comment are optional.

---

## Notifications

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/notifications` | User | List my notifications |
| POST | `/notifications/{id}/read` | User | Mark as read |
| POST | `/notifications/read-all` | User | Mark all as read |

---

## Admin — Catalog

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/admin/catalog/categories` | Admin | List all categories |
| POST | `/admin/catalog/categories` | Admin | Create category |
| PUT | `/admin/catalog/categories/{id}` | Admin | Update category |
| DELETE | `/admin/catalog/categories/{id}` | Admin | Delete category |
| GET | `/admin/catalog/products` | Admin | List all products |
| POST | `/admin/catalog/products` | Admin | Create product |
| GET | `/admin/catalog/products/{id}` | Admin | Get product by ID |
| PUT | `/admin/catalog/products/{id}` | Admin | Update product |
| DELETE | `/admin/catalog/products/{id}` | Admin | Delete product |
| POST | `/admin/catalog/products/{id}/images` | Admin | Add product image |
| DELETE | `/admin/images/{id}` | Admin | Delete product image |

---

## Admin — Orders

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/admin/orders` | Admin | List orders (paginated, filterable) |
| GET | `/admin/orders/{id}` | Admin | Get order detail |
| POST | `/admin/orders/{id}/cancel` | Admin | Cancel a paid order |

**Filter orders:**
```
GET /api/admin/orders?status=paid&user_id=abc&limit=10&offset=0&created_after=2026-01-01
```

---

## Admin — Coupons

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/admin/coupons` | Admin | List all coupons |
| POST | `/admin/coupons` | Admin | Create coupon |
| GET | `/admin/coupons/{id}` | Admin | Get coupon detail |
| PUT | `/admin/coupons/{id}` | Admin | Update coupon |

---

## Admin — Reviews

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/admin/reviews/{id}/hide` | Admin | Hide a review |
| POST | `/admin/reviews/{id}/unhide` | Admin | Unhide a review |

---

## Admin — Audit Logs

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/admin/audit-logs` | Admin | List audit logs (paginated, filterable) |

**Filter audit logs:**
```
GET /api/admin/audit-logs?action=product.stock_updated&entity_type=product&limit=20&offset=0
```

---

## Example Flows

### Customer: Browse → Cart → Coupon → Checkout

```
1. GET  /api/catalog/products?search=oud          → browse products
2. GET  /api/catalog/products/midnight-oud         → view product detail
3. POST /api/cart/items  { product_id, quantity }   → add to cart
4. POST /api/cart/coupon { code: "SAVE10" }         → apply coupon
5. POST /api/orders/checkout                        → place order
6. GET  /api/notifications                          → see order confirmation
```

### Customer: Review a Purchased Product

```
1. POST /api/orders/checkout                        → buy the product
2. POST /api/products/midnight-oud/reviews          → leave a review
   { rating: 5, title: "Great", comment: "..." }
3. GET  /api/catalog/products/midnight-oud          → see updated rating
```

### Admin: Cancel an Order

```
1. GET  /api/admin/orders?status=paid               → find paid orders
2. POST /api/admin/orders/{id}/cancel               → cancel order
3. GET  /api/admin/audit-logs?action=order.cancelled → verify audit trail
```
