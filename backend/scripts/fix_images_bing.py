import sys
import os
import shutil
from pathlib import Path

# Ensure backend path is in sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.catalog.models import ProductImage
from app.database import SessionLocal
from bing_image_downloader import downloader

FRONTEND_PUBLIC_DIR = backend_dir.parent / "frontend" / "public" / "products"

def fix_images_bing():
    db = SessionLocal()
    images = db.query(ProductImage).filter(ProductImage.url.like("%placehold.co%")).all()
    print(f"Found {len(images)} placeholder images to fix using Bing.")
    
    # Create temp download dir
    temp_dir = backend_dir / "temp_images"
    
    for img in images:
        prod = img.product
        print(f"\nProcessing '{prod.name}'...")
        
        query = f"{prod.name} perfume bottle white background product photography"
        try:
            # Delete previous downloads if any
            if (temp_dir / query).exists():
                shutil.rmtree(temp_dir / query)
                
            downloader.download(query, limit=1, output_dir=temp_dir, adult_filter_off=False, force_replace=False, timeout=10, verbose=False)
            
            # Find the downloaded file
            downloaded_files = list((temp_dir / query).glob("*"))
            if downloaded_files:
                file_path = downloaded_files[0]
                ext = file_path.suffix
                
                # Move to frontend/public/products
                new_filename = f"{prod.slug}{ext}"
                dest_path = FRONTEND_PUBLIC_DIR / new_filename
                
                shutil.copy(file_path, dest_path)
                
                # Update database
                img.url = f"/products/{new_filename}"
                db.commit()
                print(f" Updated '{prod.name}' successfully with {new_filename}!")
            else:
                print(" No image downloaded.")
        except Exception as e:
            print(f" Error: {e}")
            
    # Cleanup temp dir
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
        
if __name__ == "__main__":
    fix_images_bing()
