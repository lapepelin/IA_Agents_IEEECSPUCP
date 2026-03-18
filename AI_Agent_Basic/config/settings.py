"""
config/settings.py
──────────────────
Carga todas las variables de configuración desde .env y system_prompt.txt.
Este es el único lugar donde se definen los parámetros del bot.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ── Cargar .env ───────────────────────────────────────────────
load_dotenv()

# ── Rutas base ────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_PATH = BASE_DIR / "config" / "system_prompt.txt"

# ── Telegram ──────────────────────────────────────────────────
TELEGRAM_TOKEN: str = os.environ["TELEGRAM_TOKEN"]

# ── LLM ──────────────────────────────────────────────────────
LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")

# ── Conversación ──────────────────────────────────────────────
MAX_HISTORY: int = int(os.getenv("MAX_HISTORY", "10"))


def load_system_prompt() -> str:
    """Lee el system prompt desde config/system_prompt.txt."""
    if not PROMPT_PATH.exists():
        raise FileNotFoundError(f"No se encontró el system prompt en: {PROMPT_PATH}")
    return PROMPT_PATH.read_text(encoding="utf-8").strip()


# Cargar el system prompt al importar el módulo
SYSTEM_PROMPT: str = load_system_prompt()
