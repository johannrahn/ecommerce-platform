# E-Commerce Backend API

A production-grade e-commerce backend built with **FastAPI**, **SQLAlchemy**, and **PostgreSQL**. Designed as a reusable platform with a perfume store demo, featuring transactional checkout, a promotions engine, product reviews, user notifications, and a full admin audit trail.

**205 tests passing** | Python 3.12 | FastAPI | PostgreSQL | Docker

---

## Key Features

- **JWT Authentication** with role-based access (customer / admin)
- **Product Catalog** with categories, images, search, and pagination
- **Shopping Cart** with real-time price calculation
- **Transactional Checkout** with row-level locking and deadlock prevention
- **Payment Simulation** with injectable provider (protocol-based)
- **Promotions Engine** — percentage and fixed coupons, max discount caps, usage limits, one-per-user rules
- **Product Reviews** — purchase-verified, one per user per product, admin moderation
- **Notifications** — order events, review moderation, mark-as-read
- **Audit Trail** — every sensitive admin action logged with metadata
- **Idempotent Checkout** — safe retries via `Idempotency-Key` header
- **Request ID Tracing** — `X-Request-ID` on every response for observability

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI 0.115 |
| ORM | SQLAlchemy 2.0 (Mapped types) |
| Database | PostgreSQL 16 |
| Migrations | Alembic |
| Auth | JWT (PyJWT) + bcrypt |
| Validation | Pydantic v2 |
| Testing | Pytest + SQLite in-memory |
| Containerization | Docker + Docker Compose |
| Logging | Python logging with request ID correlation |

---

## Architecture

**Modular monolith** — each domain is a self-contained module with its own models, schemas, service, and router. No cross-model queries between modules; interaction happens through service function calls.

```
app/
├── auth/          # Registration, login, JWT
├── users/         # Profile management
├── catalog/       # Categories, products, images
├── cart/          # Cart items, coupon attachment
├── orders/        # Checkout, order history, cancellation
├── payments/      # Payment provider protocol
├── promotions/    # Coupons, discounts, usage tracking
├── reviews/       # Ratings, moderation, aggregation
├── notifications/ # User-facing event notifications
├── audit/         # Admin action audit trail
├── middleware.py  # Request ID middleware
├── exceptions.py  # Centralized error handling
└── dependencies.py # Shared DI (DB session, auth)
```

See [docs/architecture.md](docs/architecture.md) for detailed design decisions.

---

## Business Rules

### Checkout
- Cart is locked with `SELECT FOR UPDATE` to prevent double checkout
- Product rows locked in sorted order to prevent deadlocks
- Prices snapshotted at order time (immune to later price changes)
- Stock decremented atomically; restored on payment failure
- Coupon re-validated at checkout even if applied earlier to the cart

### Promotions
- Percentage and fixed discount types
- Optional `max_discount_amount` cap for percentage coupons
- `minimum_order_amount` enforcement
- Global usage limits (`max_uses`) and per-user limits (`one_per_user`)
- Case-insensitive coupon codes

### Reviews
- Only verified purchasers can review (must have a paid order with the product)
- One review per user per product
- Admin can hide/unhide reviews; hidden reviews excluded from public listing and rating aggregation

---

## Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL 16+ (or Docker)

### Run with Docker

```bash
cd backend
cp .env.example .env
docker compose up --build
```

The API will be available at `http://localhost:8000`.

### Run Locally

```bash
cd backend
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env with your PostgreSQL credentials

alembic upgrade head
python -m seeds.seed_data
uvicorn app.main:app --reload
```

### Run Migrations

```bash
alembic upgrade head          # Apply all migrations
alembic downgrade -1          # Rollback one migration
alembic history               # View migration history
```

### Seed Demo Data

```bash
python -m seeds.seed_data
```

Creates 5 categories, 12 products, and an admin account (`admin@perfumeshop.com` / `admin1234`).

### Run Tests

```bash
python -m pytest tests/ -v
```

Tests use an in-memory SQLite database — no external services required.

---

## API Documentation

| Format | URL |
|--------|-----|
| Swagger UI | `http://localhost:8000/docs` |
| ReDoc | `http://localhost:8000/redoc` |
| Health Check | `GET /health` |

See [docs/api-overview.md](docs/api-overview.md) for endpoint summaries and example flows.

---

## Project Structure

```
backend/
├── alembic/              # Database migrations (9 versions)
│   └── versions/
├── app/                  # Application source code
│   ├── auth/
│   ├── users/
│   ├── catalog/
│   ├── cart/
│   ├── orders/
│   ├── payments/
│   ├── promotions/
│   ├── reviews/
│   ├── notifications/
│   ├── audit/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── dependencies.py
│   ├── exceptions.py
│   └── middleware.py
├── seeds/                # Demo data seeding
├── tests/                # 205 tests
├── docs/                 # Architecture and API docs
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.example
```

---

## Future Improvements

- **Wishlist / Favorites** — save products for later
- **Order status tracking** — shipped, delivered, returned states
- **Email notifications** — via background task queue (Celery/RQ)
- **Image uploads** — S3/Cloudflare R2 integration
- **Rate limiting** — per-endpoint throttling
- **Refresh tokens** — token rotation for extended sessions
- **React frontend** — customer storefront and admin dashboard
- **CI/CD pipeline** — GitHub Actions with automated testing

---

## Why This Project

This is not a tutorial CRUD app. It demonstrates:

- **Transactional safety** — row-level locking, deadlock prevention, atomic stock management
- **Idempotency** — safe payment retries without double-charging
- **Domain modeling** — clean module boundaries with service-layer business logic
- **Production patterns** — structured logging, request tracing, audit trails, error handling
- **Testing discipline** — 205 integration tests covering business rules, edge cases, and access control
- **Incremental delivery** — built across 11 phases, each adding a coherent feature set

See [docs/project-summary.md](docs/project-summary.md) for a recruiter-ready overview.
