import sys
import os
import time
import requests
import re
from pathlib import Path

# Ensure backend path is in sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.catalog.models import ProductImage
from app.database import SessionLocal

FRONTEND_PUBLIC_DIR = backend_dir.parent / "frontend" / "public" / "products"

def search_image_html(query):
    print(f"Searching image for: {query}")
    url = "https://html.duckduckgo.com/html/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    try:
        # Step 1: get vqd token
        res = requests.post(url, data={'q': query}, headers=headers, timeout=10)
        if res.status_code != 200:
            print(f" Failed DDG search: {res.status_code}")
            return None
        
        # Step 2: Extract an image URL from the page
        # The DuckDuckGo HTML page includes image links in the href attribute
        # like href="?u=http%3A%2F%2F...
        match = re.search(r'href="\?u=([^"]+\.(?:jpg|png|jpeg))"', res.text, re.IGNORECASE)
        if match:
            import urllib.parse
            img_url = urllib.parse.unquote(match.group(1))
            return img_url
            
        print(" No image matches found in HTML.")
        return None
    except Exception as e:
        print(f" Error: {e}")
        return None

def download_image(url, save_path):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }
    try:
        response = requests.get(url, headers=headers, stream=True, timeout=10)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return True
    except Exception as e:
        pass
    return False

def fix_images():
    db = SessionLocal()
    images = db.query(ProductImage).filter(ProductImage.url.like("%placehold.co%")).all()
    print(f"Found {len(images)} placeholder images to fix.")
    
    for img in images:
        prod = img.product
        print(f"\nProcessing '{prod.name}'...")
        
        query = f"{prod.name} perfume bottle white background product shot"
        img_url = search_image_html(query)
        
        if img_url:
            print(f" Found URL: {img_url}")
            filename = f"{prod.slug}.jpg"
            save_path = FRONTEND_PUBLIC_DIR / filename
            
            if download_image(img_url, save_path):
                img.url = f"/products/{filename}"
                db.commit()
                print(" Updated successfully!")
            else:
                print(" Download failed. Keeping placeholder.")
        else:
            print(" No image found. Keeping placeholder.")
            
        time.sleep(2)  # Delay to avoid rate limit again

if __name__ == "__main__":
    fix_images()
