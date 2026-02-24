import logging
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.warning("SUPABASE_URL or SUPABASE_KEY is missing from environment")

# Anon key — used for auth (sign up, login, verify token)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Service role key — used for all DB operations (bypasses RLS)
# Safe to use server-side only, never expose to frontend
supabase_admin: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

logger.info(f"Supabase clients initialised → {SUPABASE_URL}")
