import sys
import os
import time
from pathlib import Path
import requests
from duckduckgo_search import DDGS

# Ensure backend path is in sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.catalog.models import Category, Product, ProductImage
from app.database import SessionLocal

# Setup paths
FRONTEND_PUBLIC_DIR = backend_dir.parent / "frontend" / "public" / "products"
FRONTEND_PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

PERFUMES = [
    # Top 40 Famous Commercial Perfumes
    {"name": "Bleu de Chanel", "slug": "bleu-de-chanel", "category": "eau-de-parfum", "price": 130.00, "desc": "A woody aromatic fragrance for men, elegant and deeply fresh."},
    {"name": "Dior Sauvage", "slug": "dior-sauvage", "category": "eau-de-toilette", "price": 115.00, "desc": "A radically fresh composition, dictated by a name that has the ring of a manifesto."},
    {"name": "Creed Aventus", "slug": "creed-aventus", "category": "eau-de-parfum", "price": 365.00, "desc": "The exceptional Aventus was inspired by the dramatic life of a historic emperor."},
    {"name": "Acqua di Gio", "slug": "acqua-di-gio", "category": "eau-de-toilette", "price": 85.00, "desc": "A resolute and aquatic fragrance, born from the sea, the sun, the earth, and the breeze of a Mediterranean island."},
    {"name": "Terre d'Hermes", "slug": "terre-d-hermes", "category": "eau-de-toilette", "price": 120.00, "desc": "A symbolic narrative revolving around matter and its transformation."},
    {"name": "Tom Ford Oud Wood", "slug": "tom-ford-oud-wood", "category": "eau-de-parfum", "price": 270.00, "desc": "One of the most rare, precious, and expensive ingredients in a perfumer's arsenal."},
    {"name": "Baccarat Rouge 540", "slug": "baccarat-rouge-540", "category": "eau-de-parfum", "price": 325.00, "desc": "Luminous and sophisticated, Baccarat Rouge 540 lays on the skin like an amber floral and woody breeze."},
    {"name": "Santal 33", "slug": "santal-33", "category": "eau-de-parfum", "price": 210.00, "desc": "A perfume that touches the sensual universality of this icon... that would intoxicate a man as much as a woman."},
    {"name": "Jo Malone Wood Sage & Sea Salt", "slug": "jo-malone-wood-sage", "category": "cologne", "price": 155.00, "desc": "Escape the everyday along the windswept shore. Waves breaking white, the air fresh with sea salt and spray."},
    {"name": "Yves Saint Laurent Y", "slug": "ysl-y", "category": "eau-de-parfum", "price": 125.00, "desc": "A bold, masculine fragrance for the man who dares to follow his passions."},
    {"name": "Chanel No. 5", "slug": "chanel-no-5", "category": "eau-de-parfum", "price": 135.00, "desc": "The very essence of femininity. A powdery floral bouquet housed in an iconic bottle."},
    {"name": "Black Opium", "slug": "black-opium", "category": "eau-de-parfum", "price": 120.00, "desc": "The highly addictive feminine fragrance from Yves Saint Laurent. Fascinating and seductively intoxicating."},
    {"name": "La Vie Est Belle", "slug": "la-vie-est-belle", "category": "eau-de-parfum", "price": 105.00, "desc": "A universal declaration to the beauty of life, composed of a luminous and solid center."},
    {"name": "Flowerbomb", "slug": "flowerbomb", "category": "eau-de-parfum", "price": 115.00, "desc": "An explosive floral bouquet. A profusion of flowers that has the power to make everything seem more positive."},
    {"name": "Daisy Marc Jacobs", "slug": "daisy-marc-jacobs", "category": "eau-de-toilette", "price": 95.00, "desc": "Radiant and enhancing, like a sparkling floral bouquet, spirited and fresh."},
    {"name": "Good Girl Carolina Herrera", "slug": "good-girl-carolina-herrera", "category": "eau-de-parfum", "price": 130.00, "desc": "A bold and highly sophisticated fragrance, inspired by Carolina's unique vision of the duality of the modern woman."},
    {"name": "Dior J'adore", "slug": "dior-jadore", "category": "eau-de-parfum", "price": 140.00, "desc": "The magnificent floral bouquet of J'adore is an artfully balanced composition where no single flower dominates."},
    {"name": "Tom Ford Black Orchid", "slug": "tom-ford-black-orchid", "category": "eau-de-parfum", "price": 150.00, "desc": "A luxurious and sensual fragrance of rich, dark accords and an alluring potion of black orchids and spice."},
    {"name": "Maison Margiela Replica Jazz Club", "slug": "replica-jazz-club", "category": "eau-de-toilette", "price": 145.00, "desc": "A woody and spicy fragrance that reminisces of an anthology of classic cocktails and coppery tones."},
    {"name": "Versace Eros", "slug": "versace-eros", "category": "eau-de-toilette", "price": 90.00, "desc": "A fragrance that interprets the sublime masculinity through a luminous aura with an intense, vibrant and glowing freshness."},
    {"name": "Paco Rabanne 1 Million", "slug": "paco-rabanne-1-million", "category": "eau-de-toilette", "price": 85.00, "desc": "A spicy leather scent that evokes fantasy and desire, arousing every envy."},
    {"name": "Giorgio Armani Si", "slug": "giorgio-armani-si", "category": "eau-de-parfum", "price": 110.00, "desc": "Chic, voluptuous, intense, and soft at the same time, Si is a chypre scent reinvented."},
    {"name": "Dolce & Gabbana Light Blue", "slug": "light-blue", "category": "eau-de-toilette", "price": 88.00, "desc": "A stunning perfume, overwhelming and irresistible like the joy of living."},
    {"name": "Gucci Bloom", "slug": "gucci-bloom", "category": "eau-de-parfum", "price": 135.00, "desc": "Capturing the spirit of the contemporary, diverse, and authentic women of Gucci."},
    {"name": "Narciso Rodriguez For Her", "slug": "narciso-for-her", "category": "eau-de-parfum", "price": 115.00, "desc": "A rare musc at the heart of this fragrance, enveloped by rose, peach and soft amber."},
    {"name": "Mugler Alien", "slug": "mugler-alien", "category": "eau-de-parfum", "price": 120.00, "desc": "A Woody Amber Solar fragrance created from the audacious excess of two powerful notes."},
    {"name": "Byredo Gypsy Water", "slug": "byredo-gypsy-water", "category": "eau-de-parfum", "price": 190.00, "desc": "An ode to the beauty of Romani culture, its unique customs, intimate beliefs and distinguished way of living."},
    {"name": "Parfums de Marly Delina", "slug": "delina-pdm", "category": "eau-de-parfum", "price": 320.00, "desc": "A floral bouquet framing Turkish rose, lily of the valley, and peony in an elegant structure."},
    {"name": "Prada L'Homme", "slug": "prada-l-homme", "category": "eau-de-toilette", "price": 105.00, "desc": "A fragrance of pairs, of doubles, of juxtapositions and layers."},
    {"name": "Kilian Angels' Share", "slug": "kilian-angels-share", "category": "eau-de-parfum", "price": 250.00, "desc": "The most personal fragrance creation yet, inspired by the eighth-generation heir to the Hennessy cognac family."},
    {"name": "Le Labo Another 13", "slug": "le-labo-another-13", "category": "eau-de-parfum", "price": 205.00, "desc": "An addictive dirty pine potion blended with twelve other ingredients such as jasmine, moss and ambrette seeds."},
    {"name": "Jean Paul Gaultier Le Male", "slug": "jpg-le-male", "category": "eau-de-toilette", "price": 95.00, "desc": "Intensive and sensible, modern, and comfortably warm, masculine and gentle..."},
    {"name": "Hermès Twilly d'Hermès", "slug": "twilly-hermes", "category": "eau-de-parfum", "price": 105.00, "desc": "The scent for the Hermès girl, a daring fragrance woven with striking ginger and sensual tuberose."},
    {"name": "Bath & Body Works Warm Vanilla Sugar", "slug": "bbw-warm-vanilla", "category": "body-mist", "price": 15.00, "desc": "A cozy, enveloping, irresistible blend of vanilla, white orchid & sparkling sugar."},
    {"name": "Victoria's Secret Bombshell", "slug": "vs-bombshell", "category": "body-mist", "price": 25.00, "desc": "Confidence and glamour—Bombshell attitude in a bottle. Our signature, award-winning fragrance."},
    {"name": "Sol de Janeiro Brazilian Crush", "slug": "sol-de-janeiro-crush", "category": "body-mist", "price": 35.00, "desc": "An intoxicating pistachio and salted caramel fragrance body mist."},
    {"name": "Jo Malone English Pear & Freesia", "slug": "jo-malone-pear", "category": "cologne", "price": 155.00, "desc": "The essence of autumn. The sensuous freshness of just-ripe pears is wrapped in a bouquet of white freesias."},
    {"name": "CK One by Calvin Klein", "slug": "ck-one", "category": "cologne", "price": 60.00, "desc": "A naturally clean, pure, and contemporary fragrance with a refreshingly new point of view."},
    {"name": "Maison Francis Kurkdjian Grand Soir", "slug": "mfk-grand-soir", "category": "eau-de-parfum", "price": 215.00, "desc": "An amber and woody fragrance that dresses the skin with vibrant notes as you lose yourself in an energetic night."},
    {"name": "Roja Parfums Elysium", "slug": "roja-elysium", "category": "eau-de-parfum", "price": 315.00, "desc": "An ultra-fresh citrus blend with an innovative musk dry down. Extremely long-lasting."}
]

def download_image(query, save_path):
    print(f"Searching image for: {query}")
    try:
        ddgs = DDGS()
        results = list(ddgs.images(query + " perfume bottle white background product shot", max_results=1))
        if results and results[0].get("image"):
            url = results[0]["image"]
            print(f"  Found URL: {url}")
            
            # Add simple headers to avoid some 403s
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
            response = requests.get(url, headers=headers, stream=True, timeout=10)
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                return True
            else:
                print(f"  Failed to download. Status: {response.status_code}")
    except Exception as e:
        print(f"  Error: {e}")
    return False

def seed():
    db = SessionLocal()
    
    # 1. Map Categories
    cats = db.query(Category).all()
    cat_map = {c.slug: c.id for c in cats}
    
    if not cat_map:
        print("Error: No categories found. Please run seed_data.py first.")
        return

    for p in PERFUMES:
        # Check if product exists
        existing = db.query(Product).filter(Product.slug == p['slug']).first()
        if existing:
            print(f"Product '{p['name']}' already exists. Skipping.")
            continue
            
        print(f"\nProcessing '{p['name']}'...")
        
        # Determine local image path
        img_filename = f"{p['slug']}.jpg"
        img_path = FRONTEND_PUBLIC_DIR / img_filename
        img_url = f"/products/{img_filename}"
        
        # Download image
        success = download_image(p['name'], img_path)
        
        # If download failed, use a placeholder
        if not success:
            print(f"  Using placeholder for {p['name']}")
            img_url = f"https://placehold.co/600x800/eeeeee/333333?text={p['name'].replace(' ', '+')}"

        # Create Product
        cat_id = cat_map.get(p['category'])
        if not cat_id:
            # Fallback to first category if not found
            cat_id = list(cat_map.values())[0]

        prod = Product(
            name=p['name'],
            slug=p['slug'],
            description=p['desc'],
            price=p['price'],
            stock=100,  # default stock
            category_id=cat_id,
            is_active=True
        )
        db.add(prod)
        db.flush() # get product ID
        
        img = ProductImage(
            product_id=prod.id,
            url=img_url,
            is_primary=True
        )
        db.add(img)
        db.commit()
        
        print(f"  Saved '{p['name']}' to database.")
        time.sleep(1) # Be nice to DDG API

if __name__ == "__main__":
    seed()
