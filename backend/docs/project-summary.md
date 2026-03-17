# Project Summary

## E-Commerce Backend API

Production-grade e-commerce backend built with FastAPI, SQLAlchemy, and PostgreSQL. Features transactional checkout with row-level locking, a coupon/discount engine, purchase-verified reviews, user notifications, and a full admin audit trail. 205 integration tests.

---

### What It Is

A reusable e-commerce platform backend (demo: perfume store) that goes well beyond basic CRUD. It implements the core business operations of a real online store: browsing, cart management, secure checkout with payment processing, promotions, product reviews, and administrative tools — all backed by a comprehensive test suite.

### Technical Challenges Solved

- **Concurrent checkout safety** — `SELECT FOR UPDATE` row-level locking prevents overselling, double checkout, and deadlocks through deterministic lock ordering
- **Atomic payment flow** — stock decrement, payment processing, coupon usage recording, and notification creation happen in a single database transaction with automatic rollback on failure
- **Idempotent payments** — client-provided idempotency keys prevent duplicate charges on network retries
- **Dual coupon validation** — basic validation at cart-apply time for fast UX feedback, full re-validation at checkout for correctness
- **Purchase-verified reviews** — join query across orders and order items ensures only actual buyers can review products
- **Operational observability** — request ID tracing across all logs, structured audit trail for every admin action

### What Makes It Stronger Than a Typical CRUD Backend

| Typical CRUD | This Project |
|-------------|-------------|
| No concurrency handling | Row-level locking with deadlock prevention |
| Optimistic stock checks | Pessimistic locking with atomic decrement |
| No payment safety | Idempotency keys + transactional rollback |
| Basic auth | JWT with role-based access control |
| No audit trail | Every admin action logged with metadata |
| Manual testing | 205 automated integration tests |
| Single validation pass | Dual validation (cart + checkout) for coupons |
| Flat architecture | Modular monolith with clean domain boundaries |

### Tech Stack

Python 3.12 | FastAPI | SQLAlchemy 2.0 | PostgreSQL | Alembic | JWT | Pydantic v2 | Docker | Pytest

---

*Built incrementally across 11 development phases, each adding a coherent feature set with full test coverage.*
