import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("SUPABASE_DB_URL")

# Supabase Transaction Pooler (Port 6543) works best with IPv4 URIs
if "?" in DB_URL:
    full_uri = f"{DB_URL}&sslmode=require"
else:
    full_uri = f"{DB_URL}?sslmode=require"

SQL = """
-- ── Admin Sessions ──────────────────────────────────────────────────────────
-- Stores persistent BI conversations for admins

create table if not exists coffee_shop_admin_sessions (
  session_id   uuid         primary key default gen_random_uuid(),
  user_email   text         not null references coffee_shop_profiles(user_email) on delete cascade,
  history      jsonb        not null default '[]',
  created_at   timestamptz  not null default now(),
  updated_at   timestamptz  not null default now()
);

create index if not exists coffee_shop_admin_sessions_user_idx
  on coffee_shop_admin_sessions (user_email);

-- Optional: Enable RLS but since only admins call this from backend, 
-- service role will handle it.
alter table coffee_shop_admin_sessions enable row level security;

create policy "Admins can read own admin sessions"
  on coffee_shop_admin_sessions for select
  using (auth.jwt() ->> 'email' = user_email);

create policy "Admins can manage own admin sessions"
  on coffee_shop_admin_sessions for all
  using (auth.jwt() ->> 'email' = user_email);
"""

def setup_admin_memory():
    try:
        with psycopg2.connect(full_uri) as conn:
            with conn.cursor() as cur:
                print("Running SQL migration: creating coffee_shop_admin_sessions...")
                cur.execute(SQL)
                conn.commit()
                print("✅ Database migration complete: Admin memory table created.")
    except Exception as e:
        print(f"❌ Error setting up admin memory database: {e}")

if __name__ == "__main__":
    setup_admin_memory()
