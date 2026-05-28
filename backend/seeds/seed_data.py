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


def _img(path: str) -> dict:
    return {"url": path, "is_primary": True}


PRODUCTS = [
    # ── Eau de Parfum ─────────────────────────────────────────────────────────
    {
        "name": "Midnight Oud",
        "slug": "midnight-oud",
        "description": "A rich, smoky blend of oud wood, amber, and black vanilla. Mysterious and unforgettable.",
        "price": 189.99, "stock": 4, "category_slug": "eau-de-parfum",
        "images": [_img("/products/midnight-oud.jpg")],
    },
    {
        "name": "Velvet Rose",
        "slug": "velvet-rose",
        "description": "Bulgarian rose absolute layered with peony, musk, and a hint of saffron. Elegant and timeless.",
        "price": 164.99, "stock": 3, "category_slug": "eau-de-parfum",
        "images": [_img("/products/velvet-rose.jpg")],
    },
    {
        "name": "Noir Absolu",
        "slug": "noir-absolu",
        "description": "Dark leather, black pepper, and tonka bean. Bold confidence in a bottle.",
        "price": 219.99, "stock": 5, "category_slug": "eau-de-parfum",
        "images": [_img("/products/noir-absolu.jpg")],
    },
    {
        "name": "Amber Elixir",
        "slug": "amber-elixir",
        "description": "Warm amber, benzoin resin, and vanilla orchid. A cozy, enveloping scent for cold evenings.",
        "price": 149.99, "stock": 4, "category_slug": "eau-de-parfum",
        "images": [_img("/products/amber-elixir.jpg")],
    },
    {
        "name": "Santal Royale",
        "slug": "santal-royale",
        "description": "Creamy Australian sandalwood, cardamom, and iris root. Understated luxury.",
        "price": 195.00, "stock": 2, "category_slug": "eau-de-parfum",
        "images": [_img("/products/santal-33.jpg")],
    },
    {
        "name": "Black Iris",
        "slug": "black-iris",
        "description": "Iris, violet, and dark musk. A powdery-dark signature for those who defy convention.",
        "price": 175.00, "stock": 6, "category_slug": "eau-de-parfum",
        "images": [_img("/products/tom-ford-black-orchid.jpg")],
    },
    {
        "name": "La Nuit Éternelle",
        "slug": "la-nuit-eternelle",
        "description": "Ylang-ylang, black rose, and smoked woods. An intoxicating nocturnal journey.",
        "price": 210.00, "stock": 2, "category_slug": "eau-de-parfum",
        "images": [_img("/products/black-opium.jpg")],
    },
    {
        "name": "Persian Garden",
        "slug": "persian-garden",
        "description": "Rose damascena, saffron, and cedarwood. A tribute to ancient Persian perfumery.",
        "price": 185.00, "stock": 5, "category_slug": "eau-de-parfum",
        "images": [_img("/products/delina-pdm.jpg")],
    },
    {
        "name": "Encens Sacré",
        "slug": "encens-sacre",
        "description": "Frankincense tears, labdanum, and white musk. Sacred and meditative.",
        "price": 155.00, "stock": 3, "category_slug": "eau-de-parfum",
        "images": [_img("/products/mugler-alien.jpeg")],
    },
    {
        "name": "Silk & Jasmine",
        "slug": "silk-and-jasmine",
        "description": "Grand jasmine absolute, soft musk, and warm skin. A luminous floral for every hour.",
        "price": 144.99, "stock": 4, "category_slug": "eau-de-parfum",
        "images": [_img("/products/gucci-bloom.jpg")],
    },
    {
        "name": "Patchouli Empire",
        "slug": "patchouli-empire",
        "description": "Indonesian patchouli, aged cognac, and leather. For the bold and unapologetic.",
        "price": 168.00, "stock": 6, "category_slug": "eau-de-parfum",
        "images": [_img("/products/replica-jazz-club.png")],
    },
    {
        "name": "Rose Oud",
        "slug": "rose-oud",
        "description": "Taif rose oil harmonised with Cambodian oud and saffron. The ultimate Middle-Eastern luxury.",
        "price": 225.00, "stock": 3, "category_slug": "eau-de-parfum",
        "images": [_img("/products/tom-ford-oud-wood.jpg")],
    },
    {
        "name": "Tobacco & Amber",
        "slug": "tobacco-and-amber",
        "description": "Aged tobacco leaf, warm amber, and honey. A fireplace in a flacon.",
        "price": 159.99, "stock": 5, "category_slug": "eau-de-parfum",
        "images": [_img("/products/kilian-angels-share.jpg")],
    },
    {
        "name": "Crystal Oud",
        "slug": "crystal-oud",
        "description": "Transparent oud, iris, and white musk. A modern reinterpretation of a classic ingredient.",
        "price": 199.00, "stock": 4, "category_slug": "eau-de-parfum",
        "images": [_img("/products/baccarat-rouge-540.png")],
    },
    {
        "name": "Narcisse Noir",
        "slug": "narcisse-noir",
        "description": "Narcissus, dark amber, and muscs. Captivating and impossible to ignore.",
        "price": 172.00, "stock": 6, "category_slug": "eau-de-parfum",
        "images": [_img("/products/narciso-for-her.jpg")],
    },
    {
        "name": "Dark Amber",
        "slug": "dark-amber",
        "description": "Cistus labdanum, castoreum, and vanilla. Dense and resinous like aged incense.",
        "price": 145.00, "stock": 3, "category_slug": "eau-de-parfum",
        "images": [_img("/products/mfk-grand-soir.jpg")],
    },
    {
        "name": "Opium Noir",
        "slug": "opium-noir",
        "description": "Black currant, mandarin, and a deep oriental base of vanilla and patchouli.",
        "price": 182.00, "stock": 5, "category_slug": "eau-de-parfum",
        "images": [_img("/products/good-girl-carolina-herrera.jpg")],
    },
    {
        "name": "Black Velvet",
        "slug": "black-velvet",
        "description": "Blackcurrant buds, jasmine, and warm sandalwood. Smooth and luxurious.",
        "price": 162.00, "stock": 4, "category_slug": "eau-de-parfum",
        "images": [_img("/products/la-vie-est-belle.jpg")],
    },
    {
        "name": "Musc Impérial",
        "slug": "musc-imperial",
        "description": "A skin-close white musk with vetiver and bergamot. Effortlessly sensual.",
        "price": 139.99, "stock": 5, "category_slug": "eau-de-parfum",
        "images": [_img("/products/le-labo-another-13.jpg")],
    },
    {
        "name": "Oud Mystère",
        "slug": "oud-mystere",
        "description": "Smoky Laotian oud, rose, and amber resin. An opulent journey to the Far East.",
        "price": 239.99, "stock": 2, "category_slug": "eau-de-parfum",
        "images": [_img("/products/roja-elysium.jpg")],
    },

    # ── Eau de Toilette ────────────────────────────────────────────────────────
    {
        "name": "Citrus Breeze",
        "slug": "citrus-breeze",
        "description": "Bright bergamot, lemon zest, and white tea. Clean and energizing for everyday wear.",
        "price": 79.99, "stock": 7, "category_slug": "eau-de-toilette",
        "images": [_img("/products/citrus-breeze.jpg")],
    },
    {
        "name": "Ocean Drift",
        "slug": "ocean-drift",
        "description": "Sea salt, driftwood, and ambergris. The freedom of open water.",
        "price": 84.99, "stock": 5, "category_slug": "eau-de-toilette",
        "images": [_img("/products/ocean-drift.jpg")],
    },
    {
        "name": "Garden Walk",
        "slug": "garden-walk",
        "description": "Dewy green leaves, jasmine, and fresh-cut grass. A stroll through an English garden.",
        "price": 74.99, "stock": 6, "category_slug": "eau-de-toilette",
        "images": [_img("/products/garden-walk.jpg")],
    },
    {
        "name": "Mediterranean Blue",
        "slug": "mediterranean-blue",
        "description": "Aquatic notes, neroli, and cypress. Sun-drenched and effortlessly cool.",
        "price": 89.99, "stock": 8, "category_slug": "eau-de-toilette",
        "images": [_img("/products/acqua-di-gio.jpeg")],
    },
    {
        "name": "White Linen",
        "slug": "white-linen",
        "description": "Crisp aldehydes, iris, and white sandalwood. As clean as freshly pressed sheets.",
        "price": 72.00, "stock": 6, "category_slug": "eau-de-toilette",
        "images": [_img("/products/ck-one.jpg")],
    },
    {
        "name": "Aqua Vitae",
        "slug": "aqua-vitae",
        "description": "Lemon verbena, ginger, and cedar. Energising and alive from the first spray.",
        "price": 95.00, "stock": 4, "category_slug": "eau-de-toilette",
        "images": [_img("/products/light-blue.jpeg")],
    },
    {
        "name": "Summer Storm",
        "slug": "summer-storm",
        "description": "Petrichor, green tea, and light musk. The electric scent just before the rain.",
        "price": 82.00, "stock": 6, "category_slug": "eau-de-toilette",
        "images": [_img("/products/byredo-gypsy-water.webp")],
    },
    {
        "name": "Green Tea & Bamboo",
        "slug": "green-tea-and-bamboo",
        "description": "Sencha green tea, bamboo shoots, and lotus flower. Zen clarity in a bottle.",
        "price": 68.00, "stock": 7, "category_slug": "eau-de-toilette",
        "images": [_img("/products/daisy-marc-jacobs.jpg")],
    },
    {
        "name": "Neroli Bianco",
        "slug": "neroli-bianco",
        "description": "White neroli, orange blossom, and dry-down musk. Sunny and Mediterranean.",
        "price": 88.00, "stock": 5, "category_slug": "eau-de-toilette",
        "images": [_img("/products/twilly-hermes.jpeg")],
    },
    {
        "name": "Fresh Fig",
        "slug": "fresh-fig",
        "description": "Green fig leaves, fig milk, and cedarwood. Earthy and unexpectedly elegant.",
        "price": 76.00, "stock": 3, "category_slug": "eau-de-toilette",
        "images": [_img("/products/jo-malone-pear.jpg")],
    },
    {
        "name": "Vetiver Sport",
        "slug": "vetiver-sport",
        "description": "Haitian vetiver, grapefruit, and white pepper. Energetic freshness for the active lifestyle.",
        "price": 71.00, "stock": 8, "category_slug": "eau-de-toilette",
        "images": [_img("/products/dior-sauvage.jpg")],
    },
    {
        "name": "Marine Escape",
        "slug": "marine-escape",
        "description": "Sea minerals, driftwood, and ozonic notes. A voyage without a destination.",
        "price": 80.00, "stock": 6, "category_slug": "eau-de-toilette",
        "images": [_img("/products/bleu-de-chanel.jpg")],
    },
    {
        "name": "Coastal Sage",
        "slug": "coastal-sage",
        "description": "Californian sage, sea breeze, and vetiver. Wild and unpretentious.",
        "price": 75.00, "stock": 7, "category_slug": "eau-de-toilette",
        "images": [_img("/products/jo-malone-wood-sage.png")],
    },
    {
        "name": "Yuzu & Ginger",
        "slug": "yuzu-and-ginger",
        "description": "Japanese yuzu, pink ginger, and hinoki wood. A sharp, lively citrus harmony.",
        "price": 85.00, "stock": 5, "category_slug": "eau-de-toilette",
        "images": [_img("/products/prada-l-homme.jpg")],
    },
    {
        "name": "Spring Meadow",
        "slug": "spring-meadow",
        "description": "Lilac, violet leaf, and soft musk. The first warm morning of spring.",
        "price": 69.00, "stock": 8, "category_slug": "eau-de-toilette",
        "images": [_img("/products/flowerbomb.jpg")],
    },
    {
        "name": "Cool Mint",
        "slug": "cool-mint",
        "description": "Spearmint, eucalyptus, and a base of clean musk. Refreshingly bold.",
        "price": 65.00, "stock": 6, "category_slug": "eau-de-toilette",
        "images": [_img("/products/versace-eros.jpg")],
    },
    {
        "name": "Bamboo Water",
        "slug": "bamboo-water",
        "description": "Bamboo, green leaves, and watery lotus. Minimalist tranquility.",
        "price": 73.00, "stock": 7, "category_slug": "eau-de-toilette",
        "images": [_img("/products/chanel-no-5.jpg")],
    },
    {
        "name": "Citrus Grove",
        "slug": "citrus-grove",
        "description": "Blood orange, sweet mandarin, and oakmoss. A walk through a sunlit orchard.",
        "price": 77.00, "stock": 5, "category_slug": "eau-de-toilette",
        "images": [_img("/products/ysl-y.jpg")],
    },
    {
        "name": "Island Breeze",
        "slug": "island-breeze",
        "description": "Coconut water, frangipani, and warm sand. Holidays bottled for everyday.",
        "price": 91.00, "stock": 4, "category_slug": "eau-de-toilette",
        "images": [_img("/products/sol-de-janeiro-crush.jpg")],
    },
    {
        "name": "Rain & Cedar",
        "slug": "rain-and-cedar",
        "description": "Petrichor, cedarwood, and green tea. Calm and grounding after the storm.",
        "price": 83.00, "stock": 6, "category_slug": "eau-de-toilette",
        "images": [_img("/products/terre-d-hermes.jpg")],
    },

    # ── Cologne ───────────────────────────────────────────────────────────────
    {
        "name": "Fresh Neroli",
        "slug": "fresh-neroli",
        "description": "Neroli blossoms, green mandarin, and cedarwood. Effortlessly fresh.",
        "price": 59.99, "stock": 8, "category_slug": "cologne",
        "images": [_img("/products/fresh-neroli.jpg")],
    },
    {
        "name": "Vetiver Classic",
        "slug": "vetiver-classic",
        "description": "Haitian vetiver, grapefruit, and white pepper. A refined everyday cologne.",
        "price": 64.99, "stock": 9, "category_slug": "cologne",
        "images": [_img("/products/vetiver-classic.jpg")],
    },
    {
        "name": "Bergamot & Cedar",
        "slug": "bergamot-and-cedar",
        "description": "Italian bergamot, cypress, and Virginia cedar. Clean confidence from morning to night.",
        "price": 55.00, "stock": 7, "category_slug": "cologne",
        "images": [_img("/products/versace-eros.jpg")],
    },
    {
        "name": "Lemon Grove",
        "slug": "lemon-grove",
        "description": "Sicilian lemon, rosemary, and light musk. Simple and immensely wearable.",
        "price": 49.99, "stock": 9, "category_slug": "cologne",
        "images": [_img("/products/citrus-breeze.jpg")],
    },
    {
        "name": "Classic Fern",
        "slug": "classic-fern",
        "description": "Lavender, oakmoss, and coumarin. A tribute to the original masculine fougère.",
        "price": 58.00, "stock": 6, "category_slug": "cologne",
        "images": [_img("/products/jpg-le-male.jpeg")],
    },
    {
        "name": "Bay Rum",
        "slug": "bay-rum",
        "description": "Bay leaf, dark rum, and clove. A classic barbershop icon reinvented.",
        "price": 52.00, "stock": 5, "category_slug": "cologne",
        "images": [_img("/products/paco-rabanne-1-million.jpg")],
    },
    {
        "name": "Sport Active",
        "slug": "sport-active",
        "description": "Citrus burst, mint, and dry cedar. Designed for the man always in motion.",
        "price": 45.99, "stock": 8, "category_slug": "cologne",
        "images": [_img("/products/dior-sauvage.jpg")],
    },
    {
        "name": "Urban Night",
        "slug": "urban-night",
        "description": "Black pepper, suede, and dark woods. The city after dark.",
        "price": 67.00, "stock": 6, "category_slug": "cologne",
        "images": [_img("/products/bleu-de-chanel.jpg")],
    },
    {
        "name": "Pine & Smoke",
        "slug": "pine-and-smoke",
        "description": "Nordic pine, birch smoke, and leather. Raw and elemental.",
        "price": 60.00, "stock": 7, "category_slug": "cologne",
        "images": [_img("/products/terre-d-hermes.jpg")],
    },
    {
        "name": "Tobacco Leaf",
        "slug": "tobacco-leaf",
        "description": "Sun-dried tobacco, tonka bean, and a hint of vanilla. Warm and laid-back.",
        "price": 63.00, "stock": 4, "category_slug": "cologne",
        "images": [_img("/products/replica-jazz-club.png")],
    },
    {
        "name": "Lavender Fields",
        "slug": "lavender-fields",
        "description": "Provençal lavender, oakmoss, and sandalwood. Timeless and universally appealing.",
        "price": 48.99, "stock": 8, "category_slug": "cologne",
        "images": [_img("/products/giorgio-armani-si.jpg")],
    },
    {
        "name": "Sage & Thyme",
        "slug": "sage-and-thyme",
        "description": "Wild sage, garden thyme, and clean musk. Herbal and vibrant.",
        "price": 50.00, "stock": 7, "category_slug": "cologne",
        "images": [_img("/products/jo-malone-wood-sage.png")],
    },
    {
        "name": "Cedar Mountain",
        "slug": "cedar-mountain",
        "description": "Rocky mountain cedar, pine needles, and vetiver. Breathe the altitude.",
        "price": 57.00, "stock": 9, "category_slug": "cologne",
        "images": [_img("/products/santal-33.jpg")],
    },
    {
        "name": "Grapefruit Splash",
        "slug": "grapefruit-splash",
        "description": "Pink grapefruit, sea salt, and white musk. Sharp, bright, and addictive.",
        "price": 44.99, "stock": 8, "category_slug": "cologne",
        "images": [_img("/products/light-blue.jpeg")],
    },
    {
        "name": "Black Pepper",
        "slug": "black-pepper",
        "description": "Tellicherry black pepper, sandalwood, and labdanum. Spicy and irresistibly modern.",
        "price": 61.00, "stock": 6, "category_slug": "cologne",
        "images": [_img("/products/ysl-y.jpg")],
    },
    {
        "name": "Morning Dew",
        "slug": "morning-dew",
        "description": "Dew drops on fresh herbs, green apple, and cedar. The scent of a clear sunrise.",
        "price": 47.00, "stock": 7, "category_slug": "cologne",
        "images": [_img("/products/ck-one.jpg")],
    },
    {
        "name": "Clean Cotton",
        "slug": "clean-cotton",
        "description": "Clean cotton musk, soft iris, and blonde woods. Crisp, unobtrusive, perfect.",
        "price": 42.99, "stock": 9, "category_slug": "cologne",
        "images": [_img("/products/byredo-gypsy-water.webp")],
    },
    {
        "name": "Herbal Garden",
        "slug": "herbal-garden",
        "description": "Rosemary, basil, and lime. A kitchen garden after summer rain.",
        "price": 46.00, "stock": 5, "category_slug": "cologne",
        "images": [_img("/products/garden-walk.jpg")],
    },
    {
        "name": "Leather & Oak",
        "slug": "leather-and-oak",
        "description": "Soft leather, oak bark, and dark amber. Gentlemanly and distinguished.",
        "price": 68.00, "stock": 6, "category_slug": "cologne",
        "images": [_img("/products/creed-aventus.jpg")],
    },
    {
        "name": "Aqua Sport",
        "slug": "aqua-sport",
        "description": "Marine accord, green citrus, and dry woods. The modern man's aquatic.",
        "price": 43.99, "stock": 7, "category_slug": "cologne",
        "images": [_img("/products/acqua-di-gio.jpeg")],
    },

    # ── Body Mist ─────────────────────────────────────────────────────────────
    {
        "name": "Vanilla Cloud",
        "slug": "vanilla-cloud",
        "description": "Whipped vanilla, coconut milk, and soft musk. Sweet comfort all day long.",
        "price": 29.99, "stock": 8, "category_slug": "body-mist",
        "images": [_img("/products/vanilla-cloud.jpg")],
    },
    {
        "name": "Berry Blush",
        "slug": "berry-blush",
        "description": "Wild berries, pink peppercorn, and sheer woods. Playful and irresistible.",
        "price": 24.99, "stock": 7, "category_slug": "body-mist",
        "images": [_img("/products/berry-blush.jpg")],
    },
    {
        "name": "Cherry Blossom",
        "slug": "cherry-blossom",
        "description": "Sakura petals, soft musk, and sandalwood. Delicate as a spring morning.",
        "price": 27.99, "stock": 9, "category_slug": "body-mist",
        "images": [_img("/products/chanel-no-5.jpg")],
    },
    {
        "name": "Coconut Dream",
        "slug": "coconut-dream",
        "description": "Toasted coconut, ylang-ylang, and warm vanilla. A tropical lullaby.",
        "price": 22.99, "stock": 10, "category_slug": "body-mist",
        "images": [_img("/products/sol-de-janeiro-crush.jpg")],
    },
    {
        "name": "Peach Nectar",
        "slug": "peach-nectar",
        "description": "Ripe peach, apricot blossom, and warm skin musk. Sun-kissed sweetness.",
        "price": 26.99, "stock": 7, "category_slug": "body-mist",
        "images": [_img("/products/bbw-warm-vanilla.jpg")],
    },
    {
        "name": "Flower Garden",
        "slug": "flower-garden",
        "description": "Peony, rose, and lily of the valley. A bouquet you carry all day.",
        "price": 28.00, "stock": 9, "category_slug": "body-mist",
        "images": [_img("/products/gucci-bloom.jpg")],
    },
    {
        "name": "Cotton Candy",
        "slug": "cotton-candy",
        "description": "Spun sugar, raspberry, and sheer musk. Playfully sweet and utterly fun.",
        "price": 21.99, "stock": 8, "category_slug": "body-mist",
        "images": [_img("/products/vs-bombshell.jpg")],
    },
    {
        "name": "Sweet Magnolia",
        "slug": "sweet-magnolia",
        "description": "Southern magnolia, warm honey, and cashmere. Soft and impossibly inviting.",
        "price": 30.00, "stock": 10, "category_slug": "body-mist",
        "images": [_img("/products/giorgio-armani-si.jpg")],
    },
    {
        "name": "Strawberry Fields",
        "slug": "strawberry-fields",
        "description": "Fresh strawberries, cream, and soft musks. Sweet-tart joy.",
        "price": 23.99, "stock": 6, "category_slug": "body-mist",
        "images": [_img("/products/vs-bombshell.jpg")],
    },
    {
        "name": "Tropical Escape",
        "slug": "tropical-escape",
        "description": "Mango, passionfruit, and jasmine. Holiday mood in a spritz.",
        "price": 25.99, "stock": 7, "category_slug": "body-mist",
        "images": [_img("/products/sol-de-janeiro-crush.jpg")],
    },
    {
        "name": "Melon & Mint",
        "slug": "melon-and-mint",
        "description": "Honeydew melon, spearmint, and light musk. Cool and refreshing.",
        "price": 22.00, "stock": 9, "category_slug": "body-mist",
        "images": [_img("/products/daisy-marc-jacobs.jpg")],
    },
    {
        "name": "Rose Petals",
        "slug": "rose-petals",
        "description": "Moroccan rose, lychee, and powdery musk. Pure, romantic softness.",
        "price": 28.99, "stock": 8, "category_slug": "body-mist",
        "images": [_img("/products/dior-jadore.jpg")],
    },
    {
        "name": "Wildflower Bloom",
        "slug": "wildflower-bloom",
        "description": "Meadow wildflowers, violet, and green vetiver. Untamed natural beauty.",
        "price": 27.00, "stock": 6, "category_slug": "body-mist",
        "images": [_img("/products/twilly-hermes.jpeg")],
    },
    {
        "name": "Passion Fruit",
        "slug": "passion-fruit",
        "description": "Passionfruit, orange blossom, and warm musk. Exotic and uplifting.",
        "price": 24.00, "stock": 10, "category_slug": "body-mist",
        "images": [_img("/products/flowerbomb.jpg")],
    },
    {
        "name": "Honey & Almond",
        "slug": "honey-and-almond",
        "description": "Wild honey, roasted almond, and caramel musk. A dessert-like skin veil.",
        "price": 31.00, "stock": 7, "category_slug": "body-mist",
        "images": [_img("/products/bbw-warm-vanilla.jpg")],
    },
    {
        "name": "Lilac Dream",
        "slug": "lilac-dream",
        "description": "Lilac blossoms, white tea, and soft musks. Gentle, nostalgic, and beautiful.",
        "price": 26.00, "stock": 8, "category_slug": "body-mist",
        "images": [_img("/products/narciso-for-her.jpg")],
    },
    {
        "name": "Summer Peach",
        "slug": "summer-peach",
        "description": "White peach, gardenia, and warm sandalwood. A golden afternoon in a spritz.",
        "price": 23.00, "stock": 5, "category_slug": "body-mist",
        "images": [_img("/products/la-vie-est-belle.jpg")],
    },
    {
        "name": "Watermelon Fresh",
        "slug": "watermelon-fresh",
        "description": "Juicy watermelon, cucumber, and sheer aquatics. The scent of summer fun.",
        "price": 20.99, "stock": 10, "category_slug": "body-mist",
        "images": [_img("/products/jo-malone-pear.jpg")],
    },
    {
        "name": "Jasmine Breeze",
        "slug": "jasmine-breeze",
        "description": "Night-blooming jasmine, neroli, and white musk. Sensual and floaty.",
        "price": 29.00, "stock": 7, "category_slug": "body-mist",
        "images": [_img("/products/delina-pdm.jpg")],
    },
    {
        "name": "Pink Grapefruit",
        "slug": "pink-grapefruit",
        "description": "Sparkling pink grapefruit, hibiscus, and light cedar. Sharp, citrusy happiness.",
        "price": 22.99, "stock": 9, "category_slug": "body-mist",
        "images": [_img("/products/berry-blush.jpg")],
    },

    # ── Gift Sets ─────────────────────────────────────────────────────────────
    {
        "name": "Discovery Collection",
        "slug": "discovery-collection",
        "description": "Five 10ml travel sprays featuring our bestsellers. The perfect introduction to our house.",
        "price": 89.99, "stock": 5, "category_slug": "gift-sets",
        "images": [_img("/products/discovery-collection.jpg")],
    },
    {
        "name": "Luxury Trio",
        "slug": "luxury-trio",
        "description": "Three full-size Eau de Parfums presented in a silk-lined box. A statement gift.",
        "price": 275.00, "stock": 4, "category_slug": "gift-sets",
        "images": [_img("/products/baccarat-rouge-540.png")],
    },
    {
        "name": "The Signature Set",
        "slug": "the-signature-set",
        "description": "Our two signature EDP fragrances plus a matching body lotion. Layering perfected.",
        "price": 195.00, "stock": 3, "category_slug": "gift-sets",
        "images": [_img("/products/roja-elysium.jpg")],
    },
    {
        "name": "Weekend Escape Kit",
        "slug": "weekend-escape-kit",
        "description": "A curated travel pouch with four 15ml favorites for every destination.",
        "price": 115.00, "stock": 6, "category_slug": "gift-sets",
        "images": [_img("/products/discovery-collection.jpg")],
    },
    {
        "name": "Grand Voyage Set",
        "slug": "grand-voyage-set",
        "description": "Six travel-size perfumes inspired by iconic world destinations.",
        "price": 145.00, "stock": 4, "category_slug": "gift-sets",
        "images": [_img("/products/mfk-grand-soir.jpg")],
    },
    {
        "name": "The Connoisseur Box",
        "slug": "the-connoisseur-box",
        "description": "Eight rare and exclusive perfumes selected by our master perfumer. The ultimate collection.",
        "price": 399.99, "stock": 2, "category_slug": "gift-sets",
        "images": [_img("/products/creed-aventus.jpg")],
    },
    {
        "name": "His & Hers Duo",
        "slug": "his-and-hers-duo",
        "description": "One feminine and one masculine EDP, beautifully boxed for couples.",
        "price": 159.99, "stock": 5, "category_slug": "gift-sets",
        "images": [_img("/products/chanel-no-5.jpg")],
    },
    {
        "name": "Traveler's Collection",
        "slug": "travelers-collection",
        "description": "Compact 15ml duo in a leather travel case. Luxury on the move.",
        "price": 99.00, "stock": 4, "category_slug": "gift-sets",
        "images": [_img("/products/discovery-collection.jpg")],
    },
    {
        "name": "Holiday Treasure Set",
        "slug": "holiday-treasure-set",
        "description": "Seasonal limited edition — three festive scents in a gold gift box.",
        "price": 175.00, "stock": 1, "category_slug": "gift-sets",
        "images": [_img("/products/kilian-angels-share.jpg")],
    },
    {
        "name": "The Noir Collection",
        "slug": "the-noir-collection",
        "description": "Four dark and mysterious EDP fragrances housed in a matte black presentation box.",
        "price": 229.00, "stock": 6, "category_slug": "gift-sets",
        "images": [_img("/products/black-opium.jpg")],
    },
    {
        "name": "Arabesque Gift Box",
        "slug": "arabesque-gift-box",
        "description": "Three oud-based fragrances in an ornate Middle-Eastern inspired box.",
        "price": 249.00, "stock": 3, "category_slug": "gift-sets",
        "images": [_img("/products/midnight-oud.jpg")],
    },
    {
        "name": "The Floral Edit",
        "slug": "the-floral-edit",
        "description": "Five floral-forward EDP and EDT fragrances selected for the flower-lover.",
        "price": 185.00, "stock": 5, "category_slug": "gift-sets",
        "images": [_img("/products/flowerbomb.jpg")],
    },
    {
        "name": "Men's Essential Set",
        "slug": "mens-essential-set",
        "description": "A cologne, an EDT, and a matching aftershave balm — everything he needs.",
        "price": 129.00, "stock": 6, "category_slug": "gift-sets",
        "images": [_img("/products/dior-sauvage.jpg")],
    },
    {
        "name": "Luxury Leather Case",
        "slug": "luxury-leather-case",
        "description": "Three EDP samples and a full-size flagship fragrance in a handstitched leather case.",
        "price": 219.00, "stock": 2, "category_slug": "gift-sets",
        "images": [_img("/products/tom-ford-black-orchid.jpg")],
    },
    {
        "name": "The Oud Collection",
        "slug": "the-oud-collection",
        "description": "Three distinct oud interpretations — light, medium, and intense — in one elegant box.",
        "price": 295.00, "stock": 4, "category_slug": "gift-sets",
        "images": [_img("/products/tom-ford-oud-wood.jpg")],
    },
    {
        "name": "Mini Wardrobe Set",
        "slug": "mini-wardrobe-set",
        "description": "Eight miniatures covering every mood and occasion. Build your signature scent wardrobe.",
        "price": 119.99, "stock": 6, "category_slug": "gift-sets",
        "images": [_img("/products/le-labo-another-13.jpg")],
    },
    {
        "name": "Bridal Gift Box",
        "slug": "bridal-gift-box",
        "description": "A romantic duo — one floral EDP plus a pearl-finish body mist — in a blush-pink box.",
        "price": 145.00, "stock": 3, "category_slug": "gift-sets",
        "images": [_img("/products/dior-jadore.jpg")],
    },
    {
        "name": "Corporate Gift Set",
        "slug": "corporate-gift-set",
        "description": "Two universally appealing EDTs with elegant, neutral packaging. Perfect for professionals.",
        "price": 105.00, "stock": 5, "category_slug": "gift-sets",
        "images": [_img("/products/versace-eros.jpg")],
    },
    {
        "name": "Anniversary Edition",
        "slug": "anniversary-edition",
        "description": "Our original signature fragrance reissued in a collector's numbered bottle. 50ml.",
        "price": 189.99, "stock": 2, "category_slug": "gift-sets",
        "images": [_img("/products/amber-elixir.jpg")],
    },
    {
        "name": "The Ultimate Wardrobe",
        "slug": "the-ultimate-wardrobe",
        "description": "Ten travel-size fragrances covering every category from our full catalog. The complete experience.",
        "price": 199.99, "stock": 3, "category_slug": "gift-sets",
        "images": [_img("/products/baccarat-rouge-540.png")],
    },
]

ADMIN_USER = {
    "email": "admin@perfumeshop.com",
    "full_name": "Store Admin",
    "hashed_password": hash_password("admin1234"),
    "role": UserRole.ADMIN,
}

EXPECTED_PRODUCT_COUNT = len(PRODUCTS)  # 100


def seed(force: bool = False):
    db = SessionLocal()
    try:
        existing_admin = db.query(User).filter(User.email == ADMIN_USER["email"]).first()

        if existing_admin:
            product_count = db.query(Product).count()
            if product_count >= EXPECTED_PRODUCT_COUNT and not force:
                print(f"Database already seeded ({product_count} products). Use --force to reseed.")
                return
            print(f"{'Force reseeding' if force else f'Found {product_count} products'} — clearing catalog...")
            db.query(ProductImage).delete()
            db.query(Product).delete()
            db.query(Category).delete()
            db.flush()
        else:
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

            print(f"  Created product: {product.name} (${product.price}, stock: {product.stock})")

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
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Force reseed even if products already exist")
    args = parser.parse_args()
    seed(force=args.force)
