import os
import logging
from telegram import Update, constants
from telegram.ext import ContextTypes
from config.settings import get_system_prompt
from src.llm_client import ask_llm
from src.document_processor import process_pdf_and_store
from src.rag_engine import get_rag_context

# Logging
logger = logging.getLogger("Handlers")

# Memoria de conversación (Short-term)
conversation_history = {}

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Primer contacto con el usuario."""
    user = update.effective_user
    chat_id = update.effective_chat.id
    conversation_history[chat_id] = []
    
    welcome = (
        f"🤖 *Agente RAG - IEEE CS PUCP (Versión PRO)*\n\n"
        f"Hola {user.first_name}. Estoy listo para asistirte.\n\n"
        "⚡ *Capacidades:*\n"
        "• Comprensión de texto con Llama 3 / Nemotron\n"
        "• Arquitectura RAG (Recuperación de Información)\n"
        "• Base de Datos Vectorial (Supabase)\n\n"
        "📩 *Prueba:* Envíame un PDF para empezar el entrenamiento."
    )
    await update.message.reply_markdown(welcome)

async def document_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja la carga y vectorización de PDFs."""
    doc = update.message.document
    chat_id = update.effective_chat.id

    if not doc.file_name.lower().endswith('.pdf'):
        await update.message.reply_text("❌ Formato no válido. Solo se aceptan PDFs.")
        return

    # Mensaje de estado inicial
    status = await update.message.reply_text("⏳ [1/3] Descargando documento de la nube de Telegram...")
    
    try:
        # Descarga
        tg_file = await context.bot.get_file(doc.file_id)
        temp_path = f"brain_data_{chat_id}.pdf"
        await tg_file.download_to_drive(temp_path)

        await status.edit_text("🧪 [2/3] Ejecutando pipeline de LangChain (Chunking & Embeddings)...")
        
        # Procesamiento RAG
        chunks = process_pdf_and_store(temp_path, doc.file_name)
        
        # Limpieza
        if os.path.exists(temp_path):
            os.remove(temp_path)

        await status.edit_text(
            f"✅ *[3/3] ¡Entrenamiento Completado!*\n\n"
            f"Archivo: `{doc.file_name}`\n"
            f"Vectores generados: `{chunks}`\n\n"
            "Ya puedes hacerme preguntas sobre este documento.",
            parse_mode=constants.ParseMode.MARKDOWN
        )

    except Exception as e:
        logger.error(f"Error en document_handler: {e}")
        await status.edit_text("⚠️ No pude procesar el documento. Verifica los logs del servidor y las llaves en el `.env`.")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja la conversación general e inyecta contexto RAG."""
    chat_id = update.effective_chat.id
    user_input = update.message.text

    if not user_input: return

    # Acción de 'escribiendo' para mejor experiencia de usuario
    await context.bot.send_chat_action(chat_id=chat_id, action=constants.ChatAction.TYPING)

    # 1. Recuperar contexto semántico
    context_text = get_rag_context(user_input)
    
    # 2. Gestionar historial
    if chat_id not in conversation_history:
        conversation_history[chat_id] = []
    
    # 3. Preparar Prompts
    system_base = get_system_prompt()
    if context_text:
        # Inyección RAG Profesional
        full_system = (
            f"{system_base}\n\n"
            "=== CONTEXTO DE DOCUMENTOS RECUPERADO ===\n"
            f"{context_text}\n"
            "=========================================="
        )
    else:
        full_system = system_base

    messages = [{"role": "system", "content": full_system}]
    
    # Añadir historial (ventan desliante de 10 msgs)
    for msg in conversation_history[chat_id][-10:]:
        messages.append(msg)
    
    # Añadir mensaje actual
    messages.append({"role": "user", "content": user_input})

    # 4. Obtener Respuesta
    response = await ask_llm(messages)

    # 5. Guardar Memoria
    conversation_history[chat_id].append({"role": "user", "content": user_input})
    conversation_history[chat_id].append({"role": "assistant", "content": response})

    # Responder
    await update.message.reply_text(response)
