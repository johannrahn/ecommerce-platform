import logging
import os

from fastapi import FastAPI

from app.audit.router import router as audit_router
from app.auth.router import router as auth_router
from app.cart.router import router as cart_router
from app.catalog.router import admin_router as catalog_admin_router
from app.catalog.router import public_router as catalog_public_router
from app.exceptions import register_exception_handlers
from app.middleware import RequestIDFilter, RequestIDMiddleware
from app.notifications.router import router as notifications_router
from app.orders.router import admin_router as orders_admin_router
from app.orders.router import router as orders_router
from app.promotions.router import admin_router as coupons_admin_router
from app.reviews.router import admin_router as reviews_admin_router
from app.reviews.router import router as reviews_router
from app.users.router import router as users_router


def create_app() -> FastAPI:
    # Configure logging with request ID
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(name)s %(levelname)s [%(request_id)s] %(message)s")
    )
    handler.addFilter(RequestIDFilter())
    logging.basicConfig(level=logging.INFO, handlers=[handler], force=True)

    app = FastAPI(
        title="E-Commerce API",
        description=(
            "Production-grade e-commerce backend with transactional checkout, "
            "promotions engine, reviews, notifications, and admin audit trail. "
            "Built with FastAPI, SQLAlchemy, and PostgreSQL."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    from fastapi.middleware.cors import CORSMiddleware

    cors_origins_env = os.getenv("CORS_ORIGINS", "*")
    cors_origins = [o.strip() for o in cors_origins_env.split(",")] if cors_origins_env != "*" else ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestIDMiddleware)
    register_exception_handlers(app)

    app.include_router(auth_router, prefix="/api")
    app.include_router(users_router, prefix="/api")
    app.include_router(catalog_public_router, prefix="/api")
    app.include_router(catalog_admin_router, prefix="/api")
    app.include_router(cart_router, prefix="/api")
    app.include_router(orders_router, prefix="/api")
    app.include_router(orders_admin_router, prefix="/api")
    app.include_router(coupons_admin_router, prefix="/api")
    app.include_router(reviews_router, prefix="/api")
    app.include_router(reviews_admin_router, prefix="/api")
    app.include_router(notifications_router, prefix="/api")
    app.include_router(audit_router, prefix="/api")

    @app.get("/health", tags=["health"])
    def health_check():
        return {"status": "ok"}

    return app


app = create_app()
