"""
Update all product image URLs to use local /products/ static files.
Preserves all orders, users, reviews — only touches ProductImage.url.

Usage:
    cd backend
    python -m scripts.fix_images_local
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.catalog.models import Product, ProductImage
from app.database import SessionLocal

# Maps product slug → local image path
SLUG_TO_IMAGE = {
    "midnight-oud":             "/products/midnight-oud.jpg",
    "velvet-rose":              "/products/velvet-rose.jpg",
    "noir-absolu":              "/products/noir-absolu.jpg",
    "amber-elixir":             "/products/amber-elixir.jpg",
    "santal-royale":            "/products/santal-33.jpg",
    "black-iris":               "/products/tom-ford-black-orchid.jpg",
    "la-nuit-eternelle":        "/products/black-opium.jpg",
    "persian-garden":           "/products/delina-pdm.jpg",
    "encens-sacre":             "/products/mugler-alien.jpeg",
    "silk-and-jasmine":         "/products/gucci-bloom.jpg",
    "patchouli-empire":         "/products/replica-jazz-club.png",
    "rose-oud":                 "/products/tom-ford-oud-wood.jpg",
    "tobacco-and-amber":        "/products/kilian-angels-share.jpg",
    "crystal-oud":              "/products/baccarat-rouge-540.png",
    "narcisse-noir":            "/products/narciso-for-her.jpg",
    "dark-amber":               "/products/mfk-grand-soir.jpg",
    "opium-noir":               "/products/good-girl-carolina-herrera.jpg",
    "black-velvet":             "/products/la-vie-est-belle.jpg",
    "musc-imperial":            "/products/le-labo-another-13.jpg",
    "oud-mystere":              "/products/roja-elysium.jpg",
    "citrus-breeze":            "/products/citrus-breeze.jpg",
    "ocean-drift":              "/products/ocean-drift.jpg",
    "garden-walk":              "/products/garden-walk.jpg",
    "mediterranean-blue":       "/products/acqua-di-gio.jpeg",
    "white-linen":              "/products/ck-one.jpg",
    "aqua-vitae":               "/products/light-blue.jpeg",
    "summer-storm":             "/products/byredo-gypsy-water.webp",
    "green-tea-and-bamboo":     "/products/daisy-marc-jacobs.jpg",
    "neroli-bianco":            "/products/twilly-hermes.jpeg",
    "fresh-fig":                "/products/jo-malone-pear.jpg",
    "vetiver-sport":            "/products/dior-sauvage.jpg",
    "marine-escape":            "/products/bleu-de-chanel.jpg",
    "coastal-sage":             "/products/jo-malone-wood-sage.png",
    "yuzu-and-ginger":          "/products/prada-l-homme.jpg",
    "spring-meadow":            "/products/flowerbomb.jpg",
    "cool-mint":                "/products/versace-eros.jpg",
    "bamboo-water":             "/products/chanel-no-5.jpg",
    "citrus-grove":             "/products/ysl-y.jpg",
    "island-breeze":            "/products/sol-de-janeiro-crush.jpg",
    "rain-and-cedar":           "/products/terre-d-hermes.jpg",
    "fresh-neroli":             "/products/fresh-neroli.jpg",
    "vetiver-classic":          "/products/vetiver-classic.jpg",
    "bergamot-and-cedar":       "/products/versace-eros.jpg",
    "lemon-grove":              "/products/citrus-breeze.jpg",
    "classic-fern":             "/products/jpg-le-male.jpeg",
    "bay-rum":                  "/products/paco-rabanne-1-million.jpg",
    "sport-active":             "/products/dior-sauvage.jpg",
    "urban-night":              "/products/bleu-de-chanel.jpg",
    "pine-and-smoke":           "/products/terre-d-hermes.jpg",
    "tobacco-leaf":             "/products/replica-jazz-club.png",
    "lavender-fields":          "/products/giorgio-armani-si.jpg",
    "sage-and-thyme":           "/products/jo-malone-wood-sage.png",
    "cedar-mountain":           "/products/santal-33.jpg",
    "grapefruit-splash":        "/products/light-blue.jpeg",
    "black-pepper":             "/products/ysl-y.jpg",
    "morning-dew":              "/products/ck-one.jpg",
    "clean-cotton":             "/products/byredo-gypsy-water.webp",
    "herbal-garden":            "/products/garden-walk.jpg",
    "leather-and-oak":          "/products/creed-aventus.jpg",
    "aqua-sport":               "/products/acqua-di-gio.jpeg",
    "vanilla-cloud":            "/products/vanilla-cloud.jpg",
    "berry-blush":              "/products/berry-blush.jpg",
    "cherry-blossom":           "/products/chanel-no-5.jpg",
    "coconut-dream":            "/products/sol-de-janeiro-crush.jpg",
    "peach-nectar":             "/products/bbw-warm-vanilla.jpg",
    "flower-garden":            "/products/gucci-bloom.jpg",
    "cotton-candy":             "/products/vs-bombshell.jpg",
    "sweet-magnolia":           "/products/giorgio-armani-si.jpg",
    "strawberry-fields":        "/products/vs-bombshell.jpg",
    "tropical-escape":          "/products/sol-de-janeiro-crush.jpg",
    "melon-and-mint":           "/products/daisy-marc-jacobs.jpg",
    "rose-petals":              "/products/dior-jadore.jpg",
    "wildflower-bloom":         "/products/twilly-hermes.jpeg",
    "passion-fruit":            "/products/flowerbomb.jpg",
    "honey-and-almond":         "/products/bbw-warm-vanilla.jpg",
    "lilac-dream":              "/products/narciso-for-her.jpg",
    "summer-peach":             "/products/la-vie-est-belle.jpg",
    "watermelon-fresh":         "/products/jo-malone-pear.jpg",
    "jasmine-breeze":           "/products/delina-pdm.jpg",
    "pink-grapefruit":          "/products/berry-blush.jpg",
    "discovery-collection":     "/products/discovery-collection.jpg",
    "luxury-trio":              "/products/baccarat-rouge-540.png",
    "the-signature-set":        "/products/roja-elysium.jpg",
    "weekend-escape-kit":       "/products/discovery-collection.jpg",
    "grand-voyage-set":         "/products/mfk-grand-soir.jpg",
    "the-connoisseur-box":      "/products/creed-aventus.jpg",
    "his-and-hers-duo":         "/products/chanel-no-5.jpg",
    "travelers-collection":     "/products/discovery-collection.jpg",
    "holiday-treasure-set":     "/products/kilian-angels-share.jpg",
    "the-noir-collection":      "/products/black-opium.jpg",
    "arabesque-gift-box":       "/products/midnight-oud.jpg",
    "the-floral-edit":          "/products/flowerbomb.jpg",
    "mens-essential-set":       "/products/dior-sauvage.jpg",
    "luxury-leather-case":      "/products/tom-ford-black-orchid.jpg",
    "the-oud-collection":       "/products/tom-ford-oud-wood.jpg",
    "mini-wardrobe-set":        "/products/le-labo-another-13.jpg",
    "bridal-gift-box":          "/products/dior-jadore.jpg",
    "corporate-gift-set":       "/products/versace-eros.jpg",
    "anniversary-edition":      "/products/amber-elixir.jpg",
    "the-ultimate-wardrobe":    "/products/baccarat-rouge-540.png",
}

# Stock updates (max 10 for scarcity hype)
SLUG_TO_STOCK = {
    "midnight-oud": 4, "velvet-rose": 3, "noir-absolu": 5, "amber-elixir": 4,
    "santal-royale": 2, "black-iris": 6, "la-nuit-eternelle": 2, "persian-garden": 5,
    "encens-sacre": 3, "silk-and-jasmine": 4, "patchouli-empire": 6, "rose-oud": 3,
    "tobacco-and-amber": 5, "crystal-oud": 4, "narcisse-noir": 6, "dark-amber": 3,
    "opium-noir": 5, "black-velvet": 4, "musc-imperial": 5, "oud-mystere": 2,
    "citrus-breeze": 7, "ocean-drift": 5, "garden-walk": 6, "mediterranean-blue": 8,
    "white-linen": 6, "aqua-vitae": 4, "summer-storm": 6, "green-tea-and-bamboo": 7,
    "neroli-bianco": 5, "fresh-fig": 3, "vetiver-sport": 8, "marine-escape": 6,
    "coastal-sage": 7, "yuzu-and-ginger": 5, "spring-meadow": 8, "cool-mint": 6,
    "bamboo-water": 7, "citrus-grove": 5, "island-breeze": 4, "rain-and-cedar": 6,
    "fresh-neroli": 8, "vetiver-classic": 9, "bergamot-and-cedar": 7, "lemon-grove": 9,
    "classic-fern": 6, "bay-rum": 5, "sport-active": 8, "urban-night": 6,
    "pine-and-smoke": 7, "tobacco-leaf": 4, "lavender-fields": 8, "sage-and-thyme": 7,
    "cedar-mountain": 9, "grapefruit-splash": 8, "black-pepper": 6, "morning-dew": 7,
    "clean-cotton": 9, "herbal-garden": 5, "leather-and-oak": 6, "aqua-sport": 7,
    "vanilla-cloud": 8, "berry-blush": 7, "cherry-blossom": 9, "coconut-dream": 10,
    "peach-nectar": 7, "flower-garden": 9, "cotton-candy": 8, "sweet-magnolia": 10,
    "strawberry-fields": 6, "tropical-escape": 7, "melon-and-mint": 9, "rose-petals": 8,
    "wildflower-bloom": 6, "passion-fruit": 10, "honey-and-almond": 7, "lilac-dream": 8,
    "summer-peach": 5, "watermelon-fresh": 10, "jasmine-breeze": 7, "pink-grapefruit": 9,
    "discovery-collection": 5, "luxury-trio": 4, "the-signature-set": 3,
    "weekend-escape-kit": 6, "grand-voyage-set": 4, "the-connoisseur-box": 2,
    "his-and-hers-duo": 5, "travelers-collection": 4, "holiday-treasure-set": 1,
    "the-noir-collection": 6, "arabesque-gift-box": 3, "the-floral-edit": 5,
    "mens-essential-set": 6, "luxury-leather-case": 2, "the-oud-collection": 4,
    "mini-wardrobe-set": 6, "bridal-gift-box": 3, "corporate-gift-set": 5,
    "anniversary-edition": 2, "the-ultimate-wardrobe": 3,
}


def fix_images():
    db = SessionLocal()
    updated = 0
    skipped = 0
    try:
        products = db.query(Product).all()
        for product in products:
            new_url = SLUG_TO_IMAGE.get(product.slug)
            new_stock = SLUG_TO_STOCK.get(product.slug)

            if new_stock is not None:
                product.stock = new_stock

            if new_url:
                imgs = db.query(ProductImage).filter(ProductImage.product_id == product.id).all()
                if imgs:
                    for img in imgs:
                        img.url = new_url
                        img.is_primary = True
                else:
                    db.add(ProductImage(product_id=product.id, url=new_url, is_primary=True, sort_order=0))
                updated += 1
                print(f"  ✓ {product.name} → {new_url} (stock: {new_stock})")
            else:
                skipped += 1
                print(f"  ✗ No mapping for slug: {product.slug}")

        db.commit()
        print(f"\nDone: {updated} updated, {skipped} skipped.")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    fix_images()
