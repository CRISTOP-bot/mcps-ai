"""Configuration management for the Telegram Remote Agent."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_ALLOWED_USERS = [
    int(x.strip()) for x in os.getenv("TELEGRAM_ALLOWED_USERS", "").split(",") if x.strip().isdigit()
]

# AI Server
AI_BASE_URL = os.getenv("AI_BASE_URL", "http://127.0.0.1:4096")
AI_DIRECTORY = os.getenv("AI_DIRECTORY", os.getcwd())
AI_PASSWORD = os.getenv("AI_PASSWORD", "")

# Database
DATABASE_PATH = os.getenv("DATABASE_PATH", "./data/telegram.db")

# Timeouts
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "0"))  # 0 = no timeout
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "2"))

# AI Server model
AI_MODEL_ID = os.getenv("AI_MODEL_ID", "deepseek-v4.1-flash-free")
AI_MODEL_PROVIDER = os.getenv("AI_MODEL_PROVIDER", "opencode")

# Fallback models (tried in order when current model hits token/usage limits)
AI_FALLBACK_MODELS = [
    "deepseek-v4.1-flash-free",
    "glm-5.3-flash-free",
    "iceman-free",
    "inkling-2-small-free",
    "crouton-alpha-free",
    "flint-40b-free",
    "nemotron-3.5-super-vl-free",
    "beam-free",
    "mimo-v2.6-flash-free",
    "nemotron-3.5-lightning-free",
    "big-pickle",
]

# Telegram message limits
TELEGRAM_MAX_MESSAGE_LENGTH = 4096


def validate():
    """Validate required configuration. Returns list of errors."""
    errors = []
    if not TELEGRAM_BOT_TOKEN:
        errors.append("TELEGRAM_BOT_TOKEN is required")
    if not TELEGRAM_ALLOWED_USERS:
        errors.append("TELEGRAM_ALLOWED_USERS is required (comma-separated user IDs)")
    if not AI_BASE_URL:
        errors.append("AI_BASE_URL is required")
    return errors


def get_db_path():
    """Get absolute database path."""
    p = Path(DATABASE_PATH)
    if not p.is_absolute():
        p = Path(__file__).parent / p
    p.parent.mkdir(parents=True, exist_ok=True)
    return str(p)
AI_AUTH_USER = os.getenv("AI_AUTH_USER", "opencode")
