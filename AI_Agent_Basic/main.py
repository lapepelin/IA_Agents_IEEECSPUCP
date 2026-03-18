"""
main.py
────────
Punto de entrada del AI_Agent_Basic.

Uso:
    python main.py

Requisitos:
    1. Copia .env.example → .env y completa los valores.
    2. pip install -r requirements.txt
    3. python main.py
"""

import logging
import sys
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)
from config.settings import TELEGRAM_TOKEN
from src.handlers import (
    start,
    help_command,
    reset,
    handle_message,
    error_handler,
)

# ── Logging ───────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
    stream=sys.stdout,
)
logging.getLogger("httpx").setLevel(logging.WARNING)  # silenciar logs de red verbosos
logger = logging.getLogger(__name__)


def main() -> None:
    """Inicializa y arranca el bot."""
    logger.info("Iniciando AI_Agent_Basic...")

    # Construir la aplicación
    app = (
        Application.builder()
        .token(TELEGRAM_TOKEN)
        .concurrent_updates(True)   # manejo eficiente de múltiples usuarios
        .build()
    )

    # ── Registrar handlers ────────────────────────────────────
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Handler global de errores
    app.add_error_handler(error_handler)

    # ── Iniciar polling ───────────────────────────────────────
    logger.info("Bot listo. Esperando mensajes (Ctrl+C para detener)...")
    app.run_polling(
        allowed_updates=["message"],
        drop_pending_updates=True,   # ignora mensajes acumulados al reiniciar
    )


if __name__ == "__main__":
    main()
