import os
import sys
from pathlib import Path
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") # Use service key for storage ops
BUCKET_NAME = "product-images"

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ SUPABASE_URL or SUPABASE_SERVICE_KEY not found in .env")
    sys.exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Paths
BASE_DIR = Path(__file__).parent.parent.parent
IMAGE_DIR = BASE_DIR / "frontend" / "public" / "images"

def get_public_url(filename):
    """Constructs the Supabase public URL for an object."""
    return f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}/{filename}"

def migrate():
    if not IMAGE_DIR.exists():
        print(f"❌ Image directory not found: {IMAGE_DIR}")
        return

    print(f"🚀 Starting migration from {IMAGE_DIR} to bucket '{BUCKET_NAME}'...")

    # 1. Get all images on disk
    image_files = [f for f in IMAGE_DIR.iterdir() if f.is_file() and f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp', '.svg']]
    
    # 2. Upload images
    uploaded_count = 0
    for img_path in image_files:
        filename = img_path.name
        
        try:
            with open(img_path, 'rb') as f:
                # Upsert=True allows re-running
                supabase.storage.from_(BUCKET_NAME).upload(
                    path=filename,
                    file=f,
                    file_options={"upsert": "true", "content-type": f"image/{img_path.suffix[1:]}"}
                )
            uploaded_count += 1
            print(f"✅ Uploaded: {filename}")
        except Exception as e:
            print(f"⚠️  Error uploading {filename}: {e}")

    print(f"📊 Uploaded {uploaded_count} images.")

    # 3. Update database records
    print("🔄 Updating database records...")
    
    # Fetch all products to match against disk files
    res = supabase.table("coffee_shop_products").select("id, name, image_url").execute()
    products = res.data
    
    updated_count = 0
    for product in products:
        current_url = product.get("image_url")
        if not current_url:
            continue
            
        # Extract filename from '/images/filename.jpg'
        if current_url.startswith("/images/"):
            filename = current_url.replace("/images/", "")
            new_url = get_public_url(filename)
            
            # Update the record
            try:
                supabase.table("coffee_shop_products").update({"image_url": new_url}).eq("id", product["id"]).execute()
                updated_count += 1
                print(f"✨ Updated DB for: {product['name']} -> {filename}")
            except Exception as e:
                print(f"❌ Error updating DB for {product['name']}: {e}")

    print(f"🎉 Migration complete! Updated {updated_count} database records.")

if __name__ == "__main__":
    migrate()
