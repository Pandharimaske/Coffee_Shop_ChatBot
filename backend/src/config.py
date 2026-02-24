"""
Single source of truth for all configuration.
Uses pydantic-settings — reads from .env automatically.
"""

from typing import Optional
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Environment ───────────────────────────────────────────────────────────
    env: str = "development"
    debug: bool = False
    app_name: str = "Coffee Shop Chatbot"
    app_url: str = "http://localhost:3000"
    api_port: int = 8000

    # ── Auth ──────────────────────────────────────────────────────────────────
    auth_provider: str = "supabase"           # "supabase" | "aws"
    secret_key: SecretStr = SecretStr("dev")  # set real value in prod
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # ── Supabase ──────────────────────────────────────────────────────────────
    supabase_url: str = ""
    supabase_key: str = ""                    # anon key
    supabase_service_key: str = ""            # service role key (scripts only)

    # ── LLM ───────────────────────────────────────────────────────────────────
    llm_model: str = "arcee-ai/trinity-large-preview:free"
    llm_temperature: float = 0.0
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    llm_timeout_seconds: int = 30

    # ── Embeddings ────────────────────────────────────────────────────────────
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    hf_api_key: str = ""

    # ── Pinecone ──────────────────────────────────────────────────────────────
    pinecone_api_key: str = ""
    pinecone_index_name: str = "coffee-products"
    pinecone_index_prefix: str = "coffee-shop"
    pinecone_region: str = "us-east-1"
    pinecone_dimension: int = 768

    # ── Retriever ─────────────────────────────────────────────────────────────
    retriever_default_top_k: int = 5
    retriever_max_top_k: int = 50
    retriever_timeout_seconds: int = 30
    retriever_retry_attempts: int = 3

    # ── Rate limiting ─────────────────────────────────────────────────────────
    enable_rate_limiting: bool = True
    requests_per_minute: int = 100

    # ── Monitoring ────────────────────────────────────────────────────────────
    log_level: str = "INFO"
    enable_request_logging: bool = True

    # ── LangSmith (optional) ──────────────────────────────────────────────────
    langchain_api_key: str = ""
    langsmith_tracing_v2: str = "false"
    langsmith_project: str = "coffee-shop-chatbot"

    # ── External ──────────────────────────────────────────────────────────────
    telegram_token: str = ""

    # ── Helpers ───────────────────────────────────────────────────────────────

    def is_production(self) -> bool:
        return self.env.lower() in ("production", "prod")

    def is_development(self) -> bool:
        return self.env.lower() in ("development", "dev", "local")

    def validate_required(self) -> None:
        """Raise if critical keys are missing."""
        missing = [
            name for name, val in {
                "OPENROUTER_API_KEY": self.openrouter_api_key,
                "HF_API_KEY": self.hf_api_key,
                "PINECONE_API_KEY": self.pinecone_api_key,
                "SUPABASE_URL": self.supabase_url,
                "SUPABASE_KEY": self.supabase_key,
            }.items() if not val
        ]
        if missing:
            raise ValueError(f"Missing required env vars: {', '.join(missing)}")


# ── Singleton ─────────────────────────────────────────────────────────────────

settings = Settings()


# ── Backward-compatible shim for old src/config.py class-style access ─────────
# Anything that does `from src.config import Config` keeps working.

class Config:
    ENV = settings.env
    DEBUG = settings.debug
    APP_NAME = settings.app_name
    APP_URL = settings.app_url
    API_PORT = settings.api_port

    LLM_MODEL = settings.llm_model
    LLM_TEMPERATURE = settings.llm_temperature
    OPENROUTER_API_KEY = settings.openrouter_api_key
    OPENROUTER_BASE_URL = settings.openrouter_base_url
    LLM_TIMEOUT_SECONDS = settings.llm_timeout_seconds

    EMBEDDING_MODEL = settings.embedding_model
    HF_API_KEY = settings.hf_api_key

    PINECONE_API_KEY = settings.pinecone_api_key
    PINECONE_INDEX_NAME = settings.pinecone_index_name
    PINECONE_INDEX_PREFIX = settings.pinecone_index_prefix
    PINECONE_REGION = settings.pinecone_region
    PINECONE_DIMENSION = settings.pinecone_dimension

    RETRIEVER_DEFAULT_TOP_K = settings.retriever_default_top_k
    RETRIEVER_MAX_TOP_K = settings.retriever_max_top_k
    RETRIEVER_TIMEOUT_SECONDS = settings.retriever_timeout_seconds
    RETRIEVER_RETRY_ATTEMPTS = settings.retriever_retry_attempts

    ENABLE_RATE_LIMITING = settings.enable_rate_limiting
    REQUESTS_PER_MINUTE = settings.requests_per_minute
    RATE_LIMIT_ENABLED = settings.enable_rate_limiting

    SUPABASE_URL = settings.supabase_url
    SUPABASE_KEY = settings.supabase_key

    HEALTH_CHECK_INTERVAL_SECONDS = 300
    CONNECTION_POOL_SIZE = 10
    USE_REDIS_CACHE = False
    REDIS_URL = "redis://localhost:6379/0"
    CACHE_TTL_SECONDS = 3600

    @classmethod
    def validate(cls) -> None:
        settings.validate_required()


# Convenience sub-configs (used by retriever)
class RetrieverConfig:
    default_top_k = settings.retriever_default_top_k
    max_top_k = settings.retriever_max_top_k
    timeout_seconds = settings.retriever_timeout_seconds
    retry_attempts = settings.retriever_retry_attempts
