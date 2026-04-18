
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_KEY")

supabase = create_client(url, key)

def setup_storage():
    buckets_to_setup = ["chat_images", "product-images"]
    
    try:
        # Check existing buckets
        existing_buckets = [b.name for b in supabase.storage.list_buckets()]
        
        for bucket_name in buckets_to_setup:
            if bucket_name not in existing_buckets:
                print(f"Creating bucket: {bucket_name}")
                supabase.storage.create_bucket(bucket_name, options={"public": True})
                print(f"✅ Bucket '{bucket_name}' created successfully.")
            else:
                print(f"Bucket '{bucket_name}' already exists.")
            
    except Exception as e:
        print(f"❌ Error setting up storage: {e}")

if __name__ == "__main__":
    setup_storage()
