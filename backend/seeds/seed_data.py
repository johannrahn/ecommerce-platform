"""
Seed script for demo perfume store.

Usage:
    cd backend
    python -m seeds.seed_data
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.auth.security import hash_password
from app.catalog.models import Category, Product, ProductImage
from app.database import SessionLocal
from app.users.models import User, UserRole

CATEGORIES = [
    {"name": "Eau de Parfum", "slug": "eau-de-parfum", "description": "Concentrated fragrances with 15-20% perfume oil. Long-lasting and intense."},
    {"name": "Eau de Toilette", "slug": "eau-de-toilette", "description": "Lighter fragrances with 5-15% perfume oil. Fresh and versatile for daily wear."},
    {"name": "Cologne", "slug": "cologne", "description": "Light and refreshing with 2-4% perfume oil. Perfect for a subtle touch."},
    {"name": "Body Mist", "slug": "body-mist", "description": "Ultra-light scented sprays for a soft, all-over fragrance."},
    {"name": "Gift Sets", "slug": "gift-sets", "description": "Curated perfume collections and bundles for special occasions."},
]

PRODUCTS = [
    # Eau de Parfum
    {
        "name": "Midnight Oud",
        "slug": "midnight-oud",
        "description": "A rich, smoky blend of oud wood, amber, and black vanilla. Mysterious and unforgettable.",
        "price": 129.99,
        "stock": 45,
        "category_slug": "eau-de-parfum",
        "images": [
            {"url": "https://placehold.co/600x800/1a1a2e/e0d6c8?text=Midnight+Oud", "is_primary": True},
        ],
    },
    {
        "name": "Velvet Rose",
        "slug": "velvet-rose",
        "description": "Bulgarian rose absolute layered with peony, musk, and a hint of saffron. Elegant and timeless.",
        "price": 149.99,
        "stock": 30,
        "category_slug": "eau-de-parfum",
        "images": [
            {"url": "https://placehold.co/600x800/4a0e2e/f5c6d0?text=Velvet+Rose", "is_primary": True},
        ],
    },
    {
        "name": "Noir Absolu",
        "slug": "noir-absolu",
        "description": "Dark leather, black pepper, and tonka bean. Bold confidence in a bottle.",
        "price": 159.99,
        "stock": 25,
        "category_slug": "eau-de-parfum",
        "images": [
            {"url": "https://placehold.co/600x800/0d0d0d/c0a080?text=Noir+Absolu", "is_primary": True},
        ],
    },
    {
        "name": "Amber Elixir",
        "slug": "amber-elixir",
        "description": "Warm amber, benzoin resin, and vanilla orchid. A cozy, enveloping scent for cold evenings.",
        "price": 139.99,
        "stock": 35,
        "category_slug": "eau-de-parfum",
        "images": [
            {"url": "https://placehold.co/600x800/8b5e34/f5e6d0?text=Amber+Elixir", "is_primary": True},
        ],
    },
    # Eau de Toilette
    {
        "name": "Citrus Breeze",
        "slug": "citrus-breeze",
        "description": "Bright bergamot, lemon zest, and white tea. Clean and energizing for everyday wear.",
        "price": 79.99,
        "stock": 60,
        "category_slug": "eau-de-toilette",
        "images": [
            {"url": "https://placehold.co/600x800/f0e68c/2e5a1e?text=Citrus+Breeze", "is_primary": True},
        ],
    },
    {
        "name": "Ocean Drift",
        "slug": "ocean-drift",
        "description": "Sea salt, driftwood, and ambergris. The freedom of open water.",
        "price": 84.99,
        "stock": 50,
        "category_slug": "eau-de-toilette",
        "images": [
            {"url": "https://placehold.co/600x800/1e90ff/e0f0ff?text=Ocean+Drift", "is_primary": True},
        ],
    },
    {
        "name": "Garden Walk",
        "slug": "garden-walk",
        "description": "Dewy green leaves, jasmine, and fresh-cut grass. A stroll through an English garden.",
        "price": 74.99,
        "stock": 40,
        "category_slug": "eau-de-toilette",
        "images": [
            {"url": "https://placehold.co/600x800/90ee90/1a3c1a?text=Garden+Walk", "is_primary": True},
        ],
    },
    # Cologne
    {
        "name": "Fresh Neroli",
        "slug": "fresh-neroli",
        "description": "Neroli blossoms, green mandarin, and cedarwood. Effortlessly fresh.",
        "price": 59.99,
        "stock": 70,
        "category_slug": "cologne",
        "images": [
            {"url": "https://placehold.co/600x800/fff8dc/6b8e23?text=Fresh+Neroli", "is_primary": True},
        ],
    },
    {
        "name": "Vetiver Classic",
        "slug": "vetiver-classic",
        "description": "Haitian vetiver, grapefruit, and white pepper. A refined everyday cologne.",
        "price": 64.99,
        "stock": 55,
        "category_slug": "cologne",
        "images": [
            {"url": "https://placehold.co/600x800/556b2f/f5f5dc?text=Vetiver+Classic", "is_primary": True},
        ],
    },
    # Body Mist
    {
        "name": "Vanilla Cloud",
        "slug": "vanilla-cloud",
        "description": "Whipped vanilla, coconut milk, and soft musk. Sweet comfort all day long.",
        "price": 29.99,
        "stock": 100,
        "category_slug": "body-mist",
        "images": [
            {"url": "https://placehold.co/600x800/fffaf0/d2a679?text=Vanilla+Cloud", "is_primary": True},
        ],
    },
    {
        "name": "Berry Blush",
        "slug": "berry-blush",
        "description": "Wild berries, pink peppercorn, and sheer woods. Playful and irresistible.",
        "price": 24.99,
        "stock": 90,
        "category_slug": "body-mist",
        "images": [
            {"url": "https://placehold.co/600x800/ff69b4/fff0f5?text=Berry+Blush", "is_primary": True},
        ],
    },
    # Gift Sets
    {
        "name": "Discovery Collection",
        "slug": "discovery-collection",
        "description": "Five 10ml travel sprays featuring our bestsellers. The perfect introduction to our house.",
        "price": 89.99,
        "stock": 20,
        "category_slug": "gift-sets",
        "images": [
            {"url": "https://placehold.co/600x800/daa520/1a1a1a?text=Discovery+Set", "is_primary": True},
        ],
    },
]

ADMIN_USER = {
    "email": "admin@perfumeshop.com",
    "full_name": "Store Admin",
    "hashed_password": hash_password("admin1234"),
    "role": UserRole.ADMIN,
}


def seed():
    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(User).filter(User.email == ADMIN_USER["email"]).first():
            print("Database already seeded. Skipping.")
            return

        # Admin user
        admin = User(**ADMIN_USER)
        db.add(admin)
        db.flush()
        print(f"Created admin user: {admin.email}")

        # Categories
        category_map: dict[str, Category] = {}
        for cat_data in CATEGORIES:
            cat = Category(**cat_data)
            db.add(cat)
            db.flush()
            category_map[cat.slug] = cat
            print(f"  Created category: {cat.name}")

        # Products
        for prod_data in PRODUCTS:
            cat_slug = prod_data.pop("category_slug")
            images_data = prod_data.pop("images", [])
            prod_data["category_id"] = category_map[cat_slug].id

            product = Product(**prod_data)
            db.add(product)
            db.flush()

            for img_data in images_data:
                img = ProductImage(product_id=product.id, **img_data)
                db.add(img)

            print(f"  Created product: {product.name} (${product.price})")

        db.commit()
        print(f"\nSeed complete: {len(CATEGORIES)} categories, {len(PRODUCTS)} products, 1 admin user.")
        print("Admin login: admin@perfumeshop.com / admin1234")

    except Exception as e:
        db.rollback()
        print(f"Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
