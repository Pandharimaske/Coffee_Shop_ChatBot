"""
Re-seed both Pinecone (vector DB) and Supabase (products table) with updated INR prices.

Run from the backend/ directory:
    python scripts/reseed_prices.py

What it does:
1. Deletes all existing Pinecone vectors and re-upserts with new INR prices
2. Upserts all products into Supabase coffee_shop_products table
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
load_dotenv()

from src.rag.vector_db_setup import VectorDBSetup
from supabase import create_client

DATA_FILE = os.path.join(os.path.dirname(__file__), "../data/products_data/products.jsonl")


# ── Step 1: Re-seed Pinecone ──────────────────────────────────────────────────

def reseed_pinecone():
    print("\n" + "="*50)
    print("STEP 1: Re-seeding Pinecone")
    print("="*50)

    setup = VectorDBSetup()
    df = setup.load_product_data(DATA_FILE)
    setup.create_index()

    # Delete all existing vectors so we don't end up with duplicates
    print("🗑️  Deleting all existing vectors...")
    try:
        setup.index.delete(delete_all=True)
        print("✅ Existing vectors deleted")
    except Exception as e:
        print(f"⚠️  Could not delete vectors (may be empty): {e}")

    vectors = setup.prepare_vectors(df)
    setup.upsert_vectors(vectors)
    setup.verify_index()
    print("✅ Pinecone re-seeded with INR prices")


# ── Step 2: Re-seed Supabase ──────────────────────────────────────────────────

def reseed_supabase():
    print("\n" + "="*50)
    print("STEP 2: Re-seeding Supabase")
    print("="*50)

    import json
    supabase = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_SERVICE_KEY"),
    )

    products = []
    with open(DATA_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            products.append({
                "name": data["name"],
                "category": data.get("category"),
                "description": data.get("description"),
                "price": float(data["price"]),
                "rating": float(data["rating"]) if data.get("rating") else None,
                "ingredients": data.get("ingredients", []),
                "image_url": f"/images/{data['image_path']}" if data.get("image_path") else None,
            })

    print(f"⬆️  Upserting {len(products)} products to Supabase...")
    res = supabase.table("coffee_shop_products").upsert(products, on_conflict="name").execute()

    if res.data:
        print(f"✅ Supabase updated — {len(res.data)} products upserted with INR prices")
    else:
        print("⚠️  Upsert returned no data — check if coffee_shop_products table exists")
        print("    If missing, create it via Supabase SQL Editor:")
        print("""
    CREATE TABLE IF NOT EXISTS coffee_shop_products (
      id BIGSERIAL PRIMARY KEY,
      name TEXT UNIQUE NOT NULL,
      category TEXT,
      description TEXT,
      price FLOAT NOT NULL,
      rating FLOAT,
      ingredients TEXT[],
      image_url TEXT
    );
        """)


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("🚀 Re-seeding all databases with INR prices...\n")

    reseed_pinecone()
    reseed_supabase()

    print("\n🎉 All done! Both Pinecone and Supabase now have INR prices.")
