"""
Seed Supabase products table from products.jsonl

Run once:
    python scripts/seed_products.py
"""

import json
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from supabase import create_client
import os
from dotenv import load_dotenv
load_dotenv()

# Seed script needs service role key to bypass RLS
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")  # service_role key, not anon
)

DATA_PATH = os.path.join(
    os.path.dirname(__file__),
    "../data/products_data/products.jsonl"
)


def seed():
    products = []
    with open(DATA_PATH, "r") as f:
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

    if not products:
        print("No products found in JSONL file.")
        return

    print(f"Seeding {len(products)} products...")
    res = supabase.table("coffee_shop_products").upsert(products, on_conflict="name").execute()

    if res.data:
        print(f"✅ Seeded {len(res.data)} products successfully.")
    else:
        print("⚠️  Upsert returned no data — check Supabase logs.")


if __name__ == "__main__":
    seed()
