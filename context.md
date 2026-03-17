# Context — Reusable E-Commerce Platform

## Project Overview

This project is a **reusable e-commerce platform** built for portfolio and future client work.
It includes both a **backend API** and a **frontend/admin interface**.

It is **not tied to a single store or brand**. The goal is to create a system that can be adapted quickly for different types of stores, while the demo implementation will use a **perfume store** niche for presentation.

The project should look strong enough for a junior backend portfolio, while also being practical enough to reuse as a starting point for real client projects.

---

## Main Goal

Build a solid **E-Commerce Platform** that demonstrates real full-stack and backend skills:

* authentication and authorization
* product and category management
* cart and order flow
* stock control
* admin features
* payment flow support
* temporary inventory reservation during checkout
* clean database design
* validation and error handling
* documentation and deployment readiness

The system should be designed so the store-specific parts are easy to replace later:

* store name
* logo
* color palette
* categories
* products
* banners/text
* business rules like shipping or payment options

---

## Why This Project Exists

There are two reasons for building this project:

### 1. Portfolio value

This project should help demonstrate backend ability in a way recruiters can understand quickly.
An e-commerce platform is familiar, useful, and full of real backend problems.

### 2. Reusability for future work

Several people have already asked whether a store can be built for them.
Because of that, this should not be just a one-off demo. It should become a **base platform** that can later be customized for different clients.

---

## Target Outcome

By the end, the project should be good enough to:

* showcase on GitHub as a serious portfolio project
* describe on a CV and LinkedIn
* discuss in interviews with confidence
* serve as a reusable foundation for future client stores

---

## Chosen Stack

The stack should stay practical, modern, and understandable.

### Backend

* **FastAPI**
* **SQLAlchemy**
* **PostgreSQL**
* **JWT authentication**
* **Docker + Docker Compose**
* **Pytest**
* **OpenAPI / Swagger**

### Frontend / Admin

* **React**
* likely **Vite** for setup simplicity
* admin dashboard and store frontend as part of the project

The backend is the main focus, but the project should also include a working frontend/admin experience so the whole system feels complete.

---

## Demo Niche

The demo implementation will use a **perfume store**.

This is a good choice because:

* it looks visually strong
* products are easy to understand
* categories can be clear and elegant
* it works well for a premium-looking demo
* the backend remains generic enough to reuse for other store types later

The perfume identity is only for presentation. The system itself should remain reusable.

---

## Required Core Features for V1

The first serious version should include these features.

### Public Store Features

* list products
* product detail page data
* search products
* filter by category
* shopping cart
* checkout preparation

### User Features

* register
* login/logout
* view profile
* view order history

### Admin Features

* create, update, delete products
* manage categories
* manage inventory / stock
* view orders
* update order status
* basic dashboard visibility into store operations

### Commerce / Order Features

* create orders
* reserve stock temporarily during checkout
* release reserved stock if checkout is not completed in time
* reduce real inventory when payment/order is confirmed
* support payment flow integration or payment simulation in v1

### Backend Quality Features

* JWT authentication
* role-based access (`admin`, `customer`)
* request validation
* centralized error handling
* pagination, filtering, sorting
* API documentation
* Docker setup
* seed/demo data
* tests for core logic

---

## Important Business Rule: Stock Management at Checkout

This is one of the most important parts of the project.

### V1 Implementation (current)

For v1, the system uses **direct stock decrement at checkout** instead of temporary reservations:

* items in the cart do **not** reserve stock — stock is only affected at checkout time
* at checkout, product rows are locked with `SELECT FOR UPDATE` to prevent race conditions
* stock is decremented atomically within the checkout transaction
* if payment succeeds → stock stays decremented, order marked as `paid`, cart marked `checked_out`
* if payment fails → stock is restored within the same transaction, order saved as `failed`, cart stays active for retry
* double checkout is prevented by locking the cart row with `FOR UPDATE`

This approach introduces important backend concepts:

* transactional consistency with row-level locking
* deadlock prevention (sorted lock acquisition)
* atomic state transitions
* race condition awareness
* failure recovery within transactions

### Future Enhancement (optional)

A temporary reservation system could be added later for scenarios where the user needs time to complete payment (e.g., bank transfers). This would require:

* StockReservation model with TTL
* background task for reservation expiration
* reservation-aware available stock calculation

---

## Payment Goal

The project should support payments as part of the commerce flow.

For the first serious version, the safest approach is:

* support a **payment simulation** or a **simple payment integration**
* connect payment success/failure to order state changes
* do not let payment complexity overwhelm the whole project early

The system should be designed so real payment providers can be added later.

---

## Recommended Scope for V1

The project should start with a realistic but controlled scope.

### Included in V1

* auth
* categories
* products
* cart
* inventory management
* orders
* admin panel
* basic storefront frontend
* temporary stock reservation
* payment simulation or simple payment flow
* Docker
* documentation
* seed data

### Implemented Beyond V1 Scope

Features that were originally postponed but have since been added:

* discount/coupon engine ✅ (promotions module with percentage + fixed codes)
* email notification workflows ✅ (notifications module, basic implementation)

### Still Postponed

* advanced payment integrations with full production handling
* product variants with complex combinations
* recommendation engine
* multi-vendor marketplace behavior
* microservices architecture

---

## Database Core Entities

The backend uses the following entities:

* User (with UserRole enum: admin/customer — no separate roles table)
* Category
* Product (includes `stock` field directly, no separate inventory table)
* ProductImage
* Cart (with `checked_out` boolean for lifecycle management)
* CartItem
* Order
* OrderItem (with snapshotted `unit_price`)

Not implemented (decided against for v1):

* StockReservation — checkout uses **direct stock decrement** instead of temporary reservations
* Inventory — stock is a field on Product, not a separate entity
* Payment — payment is handled via injectable `PaymentProvider` protocol, no DB entity

Possible future entities:

* Address
* Coupon
* ProductVariant
* Shipment

---

## Key Order / Checkout States

The system uses the following states (implemented):

### Order states (OrderStatus enum)

* `pending` — order created, payment not yet processed
* `paid` — payment succeeded, stock permanently deducted, cart marked checked_out
* `failed` — payment failed, stock restored, cart stays active for retry
* `cancelled` — order cancelled

### Cart lifecycle

* `checked_out = False` — active cart, user can modify items
* `checked_out = True` — cart finalized after successful payment, preserved for history
* A new cart is created lazily when the user next accesses their cart

### Payment flow

* Uses injectable `PaymentProvider` protocol (SimulatedProvider for v1)
* Payment result determines order status and stock handling
* No separate payment states table — result is applied atomically within the checkout transaction

---

## Design Principles

The project should follow these principles:

### Reusable

The platform should be generic enough to support different stores with minimal changes.

### Clean

The codebase should be understandable, organized, and easy to explain.

### Realistic

The project should solve actual backend problems, not just fake demo tasks.

### Incremental

It should be built in phases so progress stays manageable.

### Portfolio-friendly

A recruiter or interviewer should be able to look at it and immediately understand its value.

### Controlled complexity

The project should include serious features, but not become so ambitious that it never gets finished.

---

## Development Phases

### Phase 1 — Foundation ✅ COMPLETED

* project setup (FastAPI, SQLAlchemy 2.0, Alembic)
* Docker setup (PostgreSQL 16 on port 5433, Docker Compose)
* database setup with migrations
* auth system (JWT access tokens, 24h expiry, bcrypt hashing)
* User model with UserRole enum (admin/customer)
* 6 tests passing

### Phase 2 — Catalog ✅ COMPLETED

* Category and Product models with relationships
* ProductImage support
* Public routes (list, detail, search, filter by category) — slug-based
* Admin routes (CRUD) — ID-based, JWT-protected
* Seed script with 5 categories + 12 perfume products
* Pagination, filtering, search with ilike
* 23 tests passing

### Phase 3 — Cart ✅ COMPLETED

* Persistent Cart and CartItem models
* get_or_create_cart pattern (lazy creation)
* Add, update, remove, clear cart items
* No stock reservation at cart level (by design)
* 16 tests passing

### Phase 4 — Checkout + Orders + Payments ✅ COMPLETED

* Order and OrderItem models with price snapshotting
* Atomic checkout with SELECT FOR UPDATE (row-level locking)
* Deadlock prevention via sorted product ID locking
* Stock decremented at checkout, restored on payment failure
* PaymentProvider protocol + SimulatedProvider
* Cart finalization via checked_out flag
* 23 tests passing (including failure scenarios, double checkout, edge cases)

**Total: 68 tests passing across Phases 1–4. Full suite reaches 205 tests after Phase 5.**

### Phase 5 — Admin + Polish ✅ COMPLETED

* admin routes for products, categories, inventory, orders, coupons, reviews, audit logs
* promotions/coupons module (discount codes, percentage + fixed amounts)
* reviews module (customer reviews with moderation)
* notifications module
* audit logs module
* API documentation (OpenAPI/Swagger via FastAPI auto-docs)
* Docker Compose setup with PostgreSQL on port 5433

**Total: 205 tests passing across all modules.**

### Phase 6 — Frontend ✅ COMPLETED

Stack: React 19 + Vite 6 + TypeScript, Tailwind CSS 3.4 + shadcn/ui (New York), TanStack Query v5, Zustand v5, React Router v7

**Storefront (customer-facing):**
* Home page: hero with video backgrounds, brand strip, trust section (Free Shipping / Secure / Curated / Returns), category showcase, featured products
* Products listing: search, filter by category, sort, pagination
* Product detail: image gallery, quantity selector, add to cart (guest + auth), "About this Fragrance" block, reviews section, "You may also like" related products
* Cart page: full item management, guest + auth state, clear cart
* Cart drawer: slide-over panel, accessible from header badge
* Checkout page: guest auth gate (cart summary + sign-in CTA), order summary + place order for logged-in users
* Orders page + order detail page
* User profile page
* Auth: login, register, JWT in Zustand (localStorage persist)

**Admin panel:**
* Dashboard with store overview metrics
* Products CRUD (create, edit, delete, image management)
* Categories CRUD
* Orders management (view, update status)
* Coupons management
* Reviews moderation
* Audit logs viewer

**Guest Cart (Phase Next):**
* Guests can add to cart without signing in (Zustand persist → localStorage)
* Cart badge always visible with item count
* On login: guest cart items silently merged into backend cart via `Promise.allSettled`
* On logout: guest cart cleared to prevent cross-user contamination
* Unified cart hooks (`useUnifiedCart`, `useUnifiedAddToCart`, etc.) transparently route between guest store and backend API

**Local Dev Setup:**
* Backend: Docker Compose (`docker compose up -d` from `backend/`) — API on port 8000, PostgreSQL on port 5433
* Frontend: `npm run dev` from `frontend/` — Vite dev server on port 5173
* `docker-compose.yml` overrides `DATABASE_URL` to use Docker service name (`db:5432`) so API container connects correctly

---

## What Makes This Project Strong

This project is strong because it combines:

* backend fundamentals
* real business logic
* inventory control
* temporary reservation logic
* payment-related state handling
* reusable structure
* clear portfolio value
* possible future commercial use

It is much stronger than a basic CRUD app because it includes multiple connected systems and real commerce constraints.

---

## Success Criteria

The project is successful if:

* the platform works end-to-end for a demo perfume store
* admin and customer flows both work
* the code is clean enough to show publicly
* the project can be explained clearly in interviews
* the temporary reservation logic works reliably
* adapting it to a different store would be relatively fast

---

## Final Intent

This is not just a practice app.
It is meant to become:

1. a serious portfolio project
2. a proof of backend capability
3. a reusable base for future store builds
4. a system that demonstrates realistic commerce logic, not just CRUD screens
