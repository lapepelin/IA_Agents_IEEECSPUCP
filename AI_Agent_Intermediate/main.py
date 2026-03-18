import os
import sys
import logging

# Configurar logs
logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Main")

# Asegurar que el módulo src esté disponible
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from telegram.ext import Application, CommandHandler, MessageHandler, filters
    from config.settings import TELEGRAM_TOKEN
    from src.handlers import start_handler, message_handler, document_handler
except ImportError as e:
    logger.error(f"Faltan dependencias: {e}. Ejecuta 'pip install -r requirements.txt'")
    sys.exit(1)

def validate_environment():
    """Verifica que todas las variables críticas estén presentes."""
    required = [
        "TELEGRAM_TOKEN", 
        "SUPABASE_URL", 
        "SUPABASE_SERVICE_ROLE_KEY", 
        "LLM_API_KEY"
    ]
    missing = [var for var in required if not os.environ.get(var) or "tu_" in os.environ.get(var)]
    
    if missing:
        logger.error(f"❌ Faltan las siguientes variables de entorno: {', '.join(missing)}")
        logger.error("Asegúrate de configurar el archivo .env correctamente.")
        return False
    return True

def main():
    print("""
    ╔══════════════════════════════════════════════════════╗
    ║      AI AGENT INTERMEDIATE - IEEE CS PUCP 2026       ║
    ║        (Arquitectura RAG + Supabase Vector)          ║
    ╚══════════════════════════════════════════════════════╝
    """)

    if not validate_environment():
        sys.exit(1)

    # Construir Aplicación
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Rutas (Handlers)
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(MessageHandler(filters.Document.PDF, document_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    logger.info("🤖 Bot listo y escuchando en Telegram...")
    application.run_polling()

if __name__ == "__main__":
    main()
