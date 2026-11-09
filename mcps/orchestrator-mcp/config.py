"""Configuration for Orchestrator MCP - multi-agent coordination over OpenCode Server."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

AI_BASE_URL = os.getenv("AI_BASE_URL", "http://127.0.0.1:4096").rstrip("/")
AI_PASSWORD = os.getenv("AI_PASSWORD", "")
AI_AUTH_USER = os.getenv("AI_AUTH_USER", "opencode")
AI_DIRECTORY = os.getenv("AI_DIRECTORY", str(Path.home()))
AI_MODEL_ID = os.getenv("AI_MODEL_ID", "deepseek-v4.1-flash-free")
AI_MODEL_PROVIDER = os.getenv("AI_MODEL_PROVIDER", "opencode")
# 0 = no timeout (workers can run as long as needed)
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "0"))
DATABASE_PATH = os.getenv("DATABASE_PATH", str(Path(__file__).parent / "data" / "orchestra.db"))

FALLBACK_MODELS = [
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
