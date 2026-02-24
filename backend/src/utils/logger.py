import logging
from logging.handlers import RotatingFileHandler
import os

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Configure log file path
log_file = "logs/coffee_bot.log"

# Create rotating file handler (max 1MB per file, keep 3 backups)
file_handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3)
file_handler.setLevel(logging.INFO)

# Optional: also log to console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)  # Change to INFO or DEBUG if needed

# Formatter
formatter = logging.Formatter("[%(asctime)s] %(levelname)s:%(name)s:%(filename)s:%(lineno)d: %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Set up root logger
logger = logging.getLogger("coffee_bot")
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)