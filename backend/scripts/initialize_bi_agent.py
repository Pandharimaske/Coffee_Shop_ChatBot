import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Config
DB_URL = os.getenv("SUPABASE_DB_URL")

# Supabase Transaction Pooler (Port 6543) works best with IPv4 URIs
if "?" in DB_URL:
    full_uri = f"{DB_URL}&sslmode=require"
else:
    full_uri = f"{DB_URL}?sslmode=require"

SQL = """
-- ── Extensions ────────────────────────────────────────────────────────────────
create extension if not exists vector;

-- ── Schema Metadata Table ──────────────────────────────────────────────────────
create table if not exists coffee_shop_schema_metadata (
    id uuid primary key default gen_random_uuid(),
    content text not null,
    metadata jsonb not null,
    embedding vector(768)
);

-- ── Semantic Search RPC ────────────────────────────────────────────────────────
create or replace function match_schema_metadata (
  query_embedding vector(768),
  match_threshold float,
  match_count int
)
returns table (
  id uuid,
  content text,
  metadata jsonb,
  similarity float
)
language plpgsql
as $$
begin
  return query
  select
    coffee_shop_schema_metadata.id,
    coffee_shop_schema_metadata.content,
    coffee_shop_schema_metadata.metadata,
    1 - (coffee_shop_schema_metadata.embedding <=> query_embedding) as similarity
  from coffee_shop_schema_metadata
  where 1 - (coffee_shop_schema_metadata.embedding <=> query_embedding) > match_threshold
  order by similarity desc
  limit match_count;
end;
$$;

-- ── SQL Execution RPC ──────────────────────────────────────────────────────────
-- Strictly limited to SELECT for AI safety
create or replace function execute_sql_query(sql_query text)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
    result jsonb;
begin
    -- AI Safety: Only allow SELECT queries
    if sql_query !~* '^\\s*SELECT' then
        raise exception 'Only SELECT queries (read-only) are allowed for the BI Agent.';
    end if;

    -- Wrap query in jsonb_agg to return array of objects
    execute format('select coalesce(jsonb_agg(t), ''[]''::jsonb) from (%s) t', sql_query) into result;
    return result;
exception when others then
    return jsonb_build_array(jsonb_build_object('error', sqlerrm));
end;
$$;

-- ── Permissions ──────────────────────────────────────────────────────────────
-- Explicitly grant permissions to ensure PostgREST cache picks them up
grant execute on function public.execute_sql_query(text) to authenticated, service_role;
grant execute on function public.match_schema_metadata(vector, float, int) to authenticated, service_role;
"""

def initialize_bi_agent():
    print("🚀 Initializing BI Agent Database Infrastructure...")
    try:
        with psycopg2.connect(full_uri) as conn:
            with conn.cursor() as cur:
                print("Running SQL migrations...")
                cur.execute(SQL)
                conn.commit()
                print("✅ Database setup complete: table and RPCs created.")
    except Exception as e:
        print(f"❌ Initialization failed: {e}")

if __name__ == "__main__":
    initialize_bi_agent()
