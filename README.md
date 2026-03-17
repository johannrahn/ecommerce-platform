# ESSENCE E-Commerce Platform

## Overview
ESSENCE is a full-stack e-commerce application built around a perfume store demo. It combines a FastAPI backend, a React storefront, an admin dashboard, and a PostgreSQL database.

I built this project to practice and demonstrate full-stack development in a more realistic context than a basic CRUD app. It includes the core flows of an online store such as authentication, catalog browsing, cart management, checkout, orders, reviews, and admin tools.

## Features
### Customer-facing features
- Product catalog with category filtering, search, pagination, and product detail pages
- Guest cart persisted in the browser with merge into the backend cart after login
- User registration, login, profile management, and JWT-based authentication
- Authenticated checkout flow with simulated payment processing
- Order history and order detail pages
- Product reviews for verified purchasers only
- In-app notifications for order and review-related events

### Admin features
- Dashboard with order, revenue, and product overview metrics
- Category management
- Product CRUD, including image management and active/inactive state handling
- Order listing, filtering, detail view, and cancellation flow
- Coupon management with fixed and percentage discounts
- Review moderation (hide/unhide)
- Audit log viewer for sensitive admin actions

## Tech Stack
### Backend
- Python 3.12
- FastAPI
- SQLAlchemy 2.0
- Alembic
- PostgreSQL
- PyJWT
- Passlib + bcrypt
- Pytest
- Docker + Docker Compose

### Frontend
- React 19
- TypeScript
- Vite
- React Router
- TanStack Query
- Axios
- Zustand
- React Hook Form
- Zod
- Tailwind CSS
- Radix UI primitives

## Project Structure
```text
.
|-- backend/
|   |-- alembic/              # Database migration config and versioned migrations
|   |-- app/
|   |   |-- audit/            # Audit log models, services, and routes
|   |   |-- auth/             # Registration, login, JWT utilities
|   |   |-- cart/             # Persistent cart and coupon attachment
|   |   |-- catalog/          # Categories, products, product images
|   |   |-- notifications/    # User notification flows
|   |   |-- orders/           # Checkout and order logic
|   |   |-- payments/         # Simulated payment provider
|   |   |-- promotions/       # Coupons and coupon usage tracking
|   |   |-- reviews/          # Product reviews and moderation
|   |   `-- users/            # Profile and user routes
|   |-- docs/                 # Project notes
|   |-- scripts/              # Utility scripts, including extended product seeding
|   |-- seeds/                # Base seed data
|   |-- tests/                # Backend tests
|   |-- docker-compose.yml
|   |-- Dockerfile
|   `-- requirements.txt
|-- frontend/
|   |-- public/               # Static assets and product images
|   |-- src/
|   |   |-- api/              # API client modules
|   |   |-- components/       # Reusable UI and domain components
|   |   |-- config/           # Route and store configuration
|   |   |-- features/         # Storefront and admin pages
|   |   |-- hooks/            # React Query and custom hooks
|   |   |-- stores/           # Zustand auth/cart state
|   |   `-- types/            # TypeScript types
|   |-- package.json
|   `-- vite.config.ts
`-- context.md
```

## Screenshots
Add screenshots before publishing the repository:

```md
![Home Page](./docs/screenshots/home-page.png)
![Product Catalog](./docs/screenshots/product-catalog.png)
![Product Detail](./docs/screenshots/product-detail.png)
![Cart and Checkout](./docs/screenshots/cart-checkout.png)
![Admin Dashboard](./docs/screenshots/admin-dashboard.png)
![Admin Orders](./docs/screenshots/admin-orders.png)
```

Suggested captures:
- Home page hero and featured products
- Product listing with filters
- Product detail with reviews
- Cart and checkout flow
- Admin dashboard
- Admin products / orders / coupons / audit logs

## Setup Instructions
### Prerequisites
- Python 3.12+
- Node.js 20+
- npm
- Docker Desktop and Docker Compose, or a local PostgreSQL instance

### Recommended local setup
1. Start PostgreSQL from `backend/docker-compose.yml`.
2. Install backend dependencies and run migrations.
3. Seed the database.
4. Install frontend dependencies.
5. Run backend and frontend development servers.

## Installation
### 1. Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

### 2. Frontend
```bash
cd frontend
npm install
copy .env.example .env
```

## Environment Variables
### Backend (`backend/.env`)
| Variable | Required | Purpose |
|---|---|---|
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `SECRET_KEY` | Yes | JWT secret key |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Yes | Access token lifetime |
| `RESERVATION_EXPIRE_MINUTES` | No | Present in config |
| `RESERVATION_CLEANUP_INTERVAL_SECONDS` | No | Present in config |
| `DEBUG` | No | Debug flag |

Example from the repository:
```env
DATABASE_URL=postgresql://ecommerce:ecommerce@localhost:5433/ecommerce
SECRET_KEY=change-me-to-a-random-secret-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=1440
RESERVATION_EXPIRE_MINUTES=15
RESERVATION_CLEANUP_INTERVAL_SECONDS=120
DEBUG=true
```

### Frontend (`frontend/.env`)
| Variable | Required | Purpose |
|---|---|---|
| `VITE_API_BASE_URL` | Yes | Frontend base URL for the backend API |

Example:
```env
VITE_API_BASE_URL=http://localhost:8000/api
```

## Database and Migrations
The application uses PostgreSQL as the main database and Alembic for schema management.

Current migrations cover:
- users
- catalog
- carts
- orders
- idempotency keys
- coupons
- reviews
- notifications
- audit logs

Apply migrations with:
```bash
cd backend
alembic upgrade head
```

Useful commands:
```bash
alembic history
alembic downgrade -1
```

## Seed / Demo Data
There are two relevant seed flows in the repository.

### Base seed
```bash
cd backend
python -m seeds.seed_data
```
This creates:
- 1 admin user
- 5 categories
- 12 initial demo products

### Extended catalog seed
```bash
cd backend
python scripts/seed_40.py
```
This script is intended to add 40 perfume products across 4 categories and save product images into `frontend/public/products/`.

Important notes:
- `scripts/seed_40.py` depends on `requests` and `duckduckgo_search`, which are not listed in `backend/requirements.txt`
- it expects the base categories to exist first, so `python -m seeds.seed_data` should be run before it
- it does not remove the original 12 demo products from `seeds.seed_data`, so running both scripts on a fresh database does not produce an exact 40-product catalog by itself

For portfolio presentation, the current store is described as 40 real products across 4 categories.

## Demo Accounts
### Seeded admin account
Available after running `python -m seeds.seed_data`:
- Email: `admin@perfumeshop.com`
- Password: `admin1234`

### Customer account
- No customer demo account is seeded by default
- Create one through the registration form or `POST /api/auth/register`

## Running Locally
### Option A: Run PostgreSQL with Docker, backend locally, frontend locally
```bash
cd backend
docker compose up -d db
```

In a second terminal:
```bash
cd backend
.venv\Scripts\activate
alembic upgrade head
python -m seeds.seed_data
uvicorn app.main:app --reload
```

In a third terminal:
```bash
cd frontend
npm run dev
```

Application URLs:
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- PostgreSQL via Docker Compose: `localhost:5433`

### Option B: Run API and PostgreSQL with Docker Compose
```bash
cd backend
docker compose up --build -d
```

Then apply migrations and seed data inside the API container:
```bash
docker compose exec api alembic upgrade head
docker compose exec api python -m seeds.seed_data
```

Run the frontend separately:
```bash
cd frontend
npm run dev
```

## Key Technical Highlights
- Full-stack architecture with separate backend and frontend applications
- Real database setup with PostgreSQL and Alembic migrations
- Authentication and role-based access for customer and admin areas
- Storefront and admin dashboard connected to the same backend API
- Checkout and order flows with stock updates and coupon support
- Verified-purchase reviews, notifications, and admin audit logs
- Guest cart support on the frontend with persisted state

## Challenges and Learnings
- This project helped me move beyond simple CRUD projects and work on connected features across backend, frontend, and database layers.
- I learned how to structure a larger project into separate modules and keep the codebase easier to maintain.
- Building the checkout, cart, and order flow gave me more practice with business logic, validation, and database consistency.
- I also gained experience connecting a React frontend to a FastAPI backend and handling authenticated and admin-only flows.

## Future Improvements
- Replace the simulated payment provider with a real payment integration
- Add automated frontend tests
- Add image upload/storage support instead of relying on static or downloaded product images
- Add CI/CD for linting, testing, and deployment
- Improve seed tooling so the full 40-product dataset can be reproduced from a single documented command
- Add richer admin analytics and reporting
- Add wishlist or favorites functionality

## Contact / Links
- Portfolio: [johannr-portafolio.netlify.app](https://johannr-portafolio.netlify.app/)
- GitHub: [github.com/johannrahn](https://github.com/johannrahn)
- LinkedIn: [linkedin.com/in/johannrahn](https://www.linkedin.com/in/johannrahn/)
- Email: `johann.rahn@gmail.com`
