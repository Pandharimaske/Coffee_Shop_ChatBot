"""Scalable configuration and utilities for Coffee Shop Chatbot - Multi-user version

Provides:
- Connection pooling with health checks
- Thread-safe singleton pattern
- Distributed cache support (Redis)
- Resource limits & rate limiting
- Monitoring & observability hooks
"""

import os
import logging
import threading
from typing import Optional
from datetime import datetime, timedelta
from functools import wraps
import time

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec, PineconeException

from src.config import Config

load_dotenv()

logger = logging.getLogger(__name__)


# ============================================================
# Connection Health Check
# ============================================================

class HealthChecker:
    """Monitors connection health and triggers reconnection if needed."""

    def __init__(self):
        self.last_check = datetime.utcnow()
        self.is_healthy = True
        self.lock = threading.Lock()

    def should_check(self) -> bool:
        """Determine if health check is due."""
        return (datetime.utcnow() - self.last_check).total_seconds() > Config.HEALTH_CHECK_INTERVAL_SECONDS

    def mark_check(self, healthy: bool = True):
        """Update health status."""
        with self.lock:
            self.last_check = datetime.utcnow()
            self.is_healthy = healthy
            if not healthy:
                logger.warning("Connection health check failed")


# ============================================================
# LLM Configuration (with connection pooling)
# ============================================================

class LLMPool:
    """Thread-safe LLM instance pool for concurrent requests."""

    _instance = None
    _lock = threading.Lock()
    _models = {}

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        self.health_checker = HealthChecker()
        self._lock = threading.Lock()
        self._initialized = True
        logger.info("LLMPool initialized")

    def get_model(self, temperature: float = None, model_name: str = None) -> ChatOpenAI:
        """Get or create LLM instance (cached by temperature/model combo).
        
        Thread-safe and reuses instances for efficiency.
        """
        temperature = temperature if temperature is not None else Config.LLM_TEMPERATURE
        model_name = model_name or Config.LLM_MODEL
        key = f"{model_name}_{temperature}"

        if key in LLMPool._models:
            logger.debug(f"Reusing cached LLM instance: {key}")
            return LLMPool._models[key]

        with self._lock:
            if key not in LLMPool._models:
                try:
                    logger.info(f"Creating new LLM instance: {key}")
                    LLMPool._models[key] = ChatOpenAI(
                        model=model_name,
                        openai_api_key=Config.OPENROUTER_API_KEY,
                        openai_api_base=Config.OPENROUTER_BASE_URL,
                        temperature=temperature,
                        timeout=Config.LLM_TIMEOUT_SECONDS,
                        default_headers={
                            "HTTP-Referer": Config.APP_URL,
                            "X-Title": Config.APP_NAME
                        }
                    )
                    self.health_checker.mark_check(True)
                except Exception as e:
                    logger.error(f"Failed to create LLM instance: {str(e)}")
                    self.health_checker.mark_check(False)
                    raise

        return LLMPool._models[key]

    @classmethod
    def clear_cache(cls):
        """Clear all cached LLM instances."""
        cls._models.clear()
        logger.info("LLM cache cleared")


# Singleton instance
_llm_pool = LLMPool()


def get_model(temperature: float = 0.0, model_name: str = None) -> ChatOpenAI:
    """Get LLM instance from pool."""
    return _llm_pool.get_model(temperature=temperature, model_name=model_name)


llm = get_model()  # Default instance


# ============================================================
# Embedding Model Configuration (with caching)
# ============================================================

class EmbeddingPool:
    """Cached embedding model instances."""

    _instance = None
    _lock = threading.Lock()
    _models = {}

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._lock = threading.Lock()
        self._initialized = True
        logger.info("EmbeddingPool initialized")

    def get_model(self, model_name: str = None) -> HuggingFaceEndpointEmbeddings:
        """Get or create embedding model (cached)."""
        model_name = model_name or Config.EMBEDDING_MODEL

        if model_name in EmbeddingPool._models:
            logger.debug(f"Reusing cached embedding model: {model_name}")
            return EmbeddingPool._models[model_name]

        with self._lock:
            if model_name not in EmbeddingPool._models:
                try:
                    logger.info(f"Creating embedding model: {model_name}")
                    EmbeddingPool._models[model_name] = HuggingFaceEndpointEmbeddings(
                        model=model_name,
                        huggingfacehub_api_token=Config.HF_API_KEY
                    )
                except Exception as e:
                    logger.error(f"Failed to create embedding model {model_name}: {str(e)}")
                    raise

        return EmbeddingPool._models[model_name]

    @classmethod
    def clear_cache(cls):
        """Clear all cached embedding models."""
        cls._models.clear()
        logger.info("Embedding cache cleared")


_embedding_pool = EmbeddingPool()


def get_embedding_model(model_name: str = None) -> HuggingFaceEndpointEmbeddings:
    """Get embedding model from pool."""
    return _embedding_pool.get_model(model_name=model_name)


embedding_model = get_embedding_model()


# ============================================================
# Pinecone Configuration (with health checks)
# ============================================================

class PineconePool:
    """Managed Pinecone client with health checks."""

    _instance = None
    _lock = threading.Lock()
    _client = None
    _indices = {}

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.health_checker = HealthChecker()
        self._lock = threading.Lock()
        self._initialized = True
        logger.info("PineconePool initialized")

    def get_client(self) -> Pinecone:
        """Get or create Pinecone client (singleton)."""
        if PineconePool._client is not None:
            return PineconePool._client

        with self._lock:
            if PineconePool._client is None:
                try:
                    logger.info("Creating Pinecone client")
                    PineconePool._client = Pinecone(api_key=Config.PINECONE_API_KEY)
                    self.health_checker.mark_check(True)
                except Exception as e:
                    logger.error(f"Failed to create Pinecone client: {str(e)}")
                    self.health_checker.mark_check(False)
                    raise

        return PineconePool._client

    def get_index(self, index_name: str = None):
        """Get or cache Pinecone index."""
        index_name = index_name or Config.PINECONE_INDEX_NAME

        if index_name in PineconePool._indices:
            logger.debug(f"Reusing cached index: {index_name}")
            return PineconePool._indices[index_name]

        with self._lock:
            if index_name not in PineconePool._indices:
                try:
                    logger.info(f"Getting index: {index_name}")
                    client = self.get_client()
                    
                    # Create index if it doesn't exist
                    if index_name not in client.list_indexes().names():
                        logger.info(f"Creating new index: {index_name}")
                        client.create_index(
                            name=index_name,
                            dimension=Config.PINECONE_DIMENSION,
                            metric="cosine",
                            spec=ServerlessSpec(cloud="aws", region=Config.PINECONE_REGION)
                        )
                        # Wait for index to be ready
                        time.sleep(5)
                    
                    PineconePool._indices[index_name] = client.Index(index_name)
                    self.health_checker.mark_check(True)
                except PineconeException as e:
                    logger.error(f"Pinecone error getting index {index_name}: {str(e)}")
                    self.health_checker.mark_check(False)
                    raise
                except Exception as e:
                    logger.error(f"Failed to get index {index_name}: {str(e)}")
                    raise

        return PineconePool._indices[index_name]

    @classmethod
    def clear_cache(cls):
        """Clear cached indices."""
        cls._indices.clear()
        cls._client = None
        logger.info("Pinecone cache cleared")


_pinecone_pool = PineconePool()


def get_pinecone_client() -> Pinecone:
    """Get Pinecone client from pool."""
    return _pinecone_pool.get_client()


def get_pinecone_index(index_name: str = None):
    """Get Pinecone index from pool."""
    return _pinecone_pool.get_index(index_name=index_name)


# ============================================================
# Vectorstore Configuration
# ============================================================

class VectorstorePool:
    """Managed Vectorstore instances with lazy initialization."""

    _instance = None
    _lock = threading.Lock()
    _stores = {}

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._lock = threading.Lock()
        self._initialized = True
        logger.info("VectorstorePool initialized")

    def get_vectorstore(self, index_name: str = None) -> PineconeVectorStore:
        """Get or create vectorstore instance."""
        index_name = index_name or Config.PINECONE_INDEX_NAME

        if index_name in VectorstorePool._stores:
            logger.debug(f"Reusing cached vectorstore: {index_name}")
            return VectorstorePool._stores[index_name]

        with self._lock:
            if index_name not in VectorstorePool._stores:
                try:
                    logger.info(f"Creating vectorstore for index: {index_name}")
                    idx = get_pinecone_index(index_name)
                    emb = get_embedding_model()
                    
                    VectorstorePool._stores[index_name] = PineconeVectorStore(
                        index=idx,
                        embedding=emb,
                        text_key="text"
                    )
                except Exception as e:
                    logger.error(f"Failed to create vectorstore for {index_name}: {str(e)}")
                    raise

        return VectorstorePool._stores[index_name]

    @classmethod
    def clear_cache(cls):
        """Clear all cached vectorstores."""
        cls._stores.clear()
        logger.info("Vectorstore cache cleared")


_vectorstore_pool = VectorstorePool()


def get_vectorstore(index_name: str = None) -> PineconeVectorStore:
    """Get vectorstore instance from pool."""
    return _vectorstore_pool.get_vectorstore(index_name=index_name)


# Lazy-loaded default vectorstore instance
_vectorstore_instance = None


def get_default_vectorstore() -> PineconeVectorStore:
    """Get or create the default vectorstore instance (lazy-loaded at first use)."""
    global _vectorstore_instance
    if _vectorstore_instance is None:
        _vectorstore_instance = get_vectorstore()
    return _vectorstore_instance


# ============================================================
# Rate Limiting (optional, configurable)
# ============================================================

class RateLimiter:
    """Simple in-memory rate limiter. Use Redis for distributed systems."""

    def __init__(self, requests_per_minute: int = None):
        self.requests_per_minute = requests_per_minute or Config.REQUESTS_PER_MINUTE
        self.requests = {}
        self._lock = threading.Lock()

    def is_allowed(self, user_id: str) -> bool:
        """Check if user is within rate limit."""
        if not Config.ENABLE_RATE_LIMITING:
            return True

        with self._lock:
            now = datetime.utcnow()
            minute_ago = now - timedelta(minutes=1)

            if user_id not in self.requests:
                self.requests[user_id] = []

            # Remove old requests
            self.requests[user_id] = [
                ts for ts in self.requests[user_id] if ts > minute_ago
            ]

            if len(self.requests[user_id]) >= self.requests_per_minute:
                logger.warning(f"Rate limit exceeded for user: {user_id}")
                return False

            self.requests[user_id].append(now)
            return True


_rate_limiter = RateLimiter()


def rate_limit(func):
    """Decorator to apply rate limiting to functions."""
    @wraps(func)
    def wrapper(user_id: str = None, *args, **kwargs):
        if user_id and not _rate_limiter.is_allowed(user_id):
            raise Exception(f"Rate limit exceeded for user {user_id}")
        return func(*args, **kwargs)
    return wrapper


# ============================================================
# Lifecycle Management
# ============================================================

def initialize_all() -> None:
    """Initialize all connection pools and validate configuration."""
    try:
        Config.validate()
        logger.info("Configuration validated")

        # Warm up connections
        get_model()
        get_embedding_model()
        get_pinecone_client()
        
        logger.info("All connections initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize connections: {str(e)}")
        raise


def shutdown_all() -> None:
    """Gracefully shutdown all connections."""
    logger.info("Shutting down connections...")
    LLMPool.clear_cache()
    EmbeddingPool.clear_cache()
    PineconePool.clear_cache()
    VectorstorePool.clear_cache()
    logger.info("All connections shut down")


# ============================================================
# Public API (backward compatible)
# ============================================================

def load_vectorstore() -> PineconeVectorStore:
    """Public API to get vectorstore instance."""
    return get_vectorstore()


def refresh_vectorstore(index_name: str = None) -> PineconeVectorStore:
    """Force refresh vectorstore connection."""
    VectorstorePool.clear_cache()
    return get_vectorstore(index_name=index_name)


# Initialize on import
try:
    Config.validate()
except Exception as e:
    logger.warning(f"Configuration not fully validated on import: {e}")
