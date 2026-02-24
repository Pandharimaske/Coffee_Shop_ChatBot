# Single config lives in src/config.py
# This re-export keeps api/ imports working without duplication.
from src.config import settings, Config  # noqa: F401
