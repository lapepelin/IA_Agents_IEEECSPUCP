"""
src/handlers.py
────────────────
Todos los handlers de Telegram para el AI_Agent_Basic.

Comandos disponibles:
  /start  — Mensaje de bienvenida
  /help   — Ayuda y comandos disponibles
  /reset  — Limpia el historial de conversación

Flujo de mensaje:
  Usuario → Telegram → handler → LLM → respuesta → Usuario
"""

import logging
from collections import defaultdict
from telegram import Update
from telegram.ext import ContextTypes
from config.settings import SYSTEM_PROMPT, MAX_HISTORY
from src.llm_client import ask_llm

logger = logging.getLogger(__name__)

# ── Memoria conversacional ────────────────────────────────────
# Dict: { chat_id: [{"role": "...", "content": "..."}, ...] }
conversation_history: dict[int, list[dict]] = defaultdict(list)


def _get_messages(chat_id: int) -> list[dict]:
    """Construye la lista completa de mensajes: system + historial."""
    return [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history[chat_id]


import os
import json
from pathlib import Path

# ── Carpeta de conversaciones ──────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
CONVERSACIONES_DIR = BASE_DIR / "conversaciones"
CONVERSACIONES_DIR.mkdir(exist_ok=True)


def _save_history(chat_id: int) -> None:
    """Guarda el historial de un usuario en un archivo JSON."""
    filepath = CONVERSACIONES_DIR / f"{chat_id}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(conversation_history[chat_id], f, ensure_ascii=False, indent=2)


def _add_message(chat_id: int, role: str, content: str) -> None:
    """Agrega un mensaje al historial, mantiene el límite y lo guarda en disco."""
    # Filtrar mensajes nulos o vacíos para evitar que el LLM falle
    if not content:
        return
        
    conversation_history[chat_id].append({"role": role, "content": content})
    # Mantener solo los últimos MAX_HISTORY mensajes (pares user/assistant)
    if len(conversation_history[chat_id]) > MAX_HISTORY * 2:
        conversation_history[chat_id] = conversation_history[chat_id][-MAX_HISTORY * 2:]
    
    # Guardar en JSON
    _save_history(chat_id)


# ── /start ────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mensaje de bienvenida al iniciar el bot."""
    user = update.effective_user
    welcome = (
        f"¡Hola, {user.first_name}! Soy el asistente de IA del IEEE CS PUCP.\n\n"
        "Puedo ayudarte con preguntas, dudas o simplemente charlar. "
        "Solo escríbeme lo que necesites.\n\n"
        "[+] Usa /help para ver los comandos disponibles."
    )
    await update.message.reply_text(welcome)
    logger.info("Usuario %s inició el bot.", user.id)


# ── /help ─────────────────────────────────────────────────────
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Muestra los comandos disponibles."""
    help_text = (
        "Comandos disponibles:\n\n"
        "/start — Mensaje de bienvenida\n"
        "/help  — Muestra esta ayuda\n"
        "/reset — Borra el historial de conversación\n\n"
        "-> O simplemente escríbeme y responderé usando IA."
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


# ── /reset ────────────────────────────────────────────────────
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Limpia el historial de conversación del usuario."""
    chat_id = update.effective_chat.id
    conversation_history[chat_id].clear()
    await update.message.reply_text("Historial borrado. ¡Empecemos de nuevo!")
    logger.info("Historial reseteado para chat %s.", chat_id)


# ── Mensaje de texto ──────────────────────────────────────────
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler principal: recibe mensaje, llama al LLM, responde."""
    chat_id = update.effective_chat.id
    user_text = update.message.text

    # Mostrar "escribiendo..." mientras el LLM responde
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    # Guardar mensaje del usuario en historial
    _add_message(chat_id, "user", user_text)

    # Llamar al LLM con el historial completo
    try:
        response_text = await ask_llm(_get_messages(chat_id))
    except Exception as e:
        logger.error("Error en LLM para chat %s: %s", chat_id, e)
        # Remover el último mensaje del usuario para no contaminar el historial
        conversation_history[chat_id].pop()
        await update.message.reply_text(
            "[!] Tuve un problema al procesar tu mensaje. Por favor, inténtalo de nuevo."
        )
        return

    # Guardar respuesta del asistente en historial
    _add_message(chat_id, "assistant", response_text)

    await update.message.reply_text(response_text)
    logger.info("Respondido a chat %s (%d chars).", chat_id, len(response_text))


# ── Error handler ─────────────────────────────────────────────
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manejo global de errores inesperados."""
    logger.error("Error inesperado: %s", context.error, exc_info=context.error)
