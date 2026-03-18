"""
src/llm_client.py
──────────────────
Capa de abstracción para llamar al LLM.

Usa el SDK oficial de OpenAI, compatible con:
  - OpenAI (GPT-4o, GPT-4o-mini, etc.)
  - Groq (Llama 3, Mixtral, etc.)
  - OpenRouter (acceso a cientos de modelos)
  - Cualquier API compatible con la interfaz de OpenAI

Para cambiar de proveedor: solo edita LLM_BASE_URL y LLM_MODEL en tu .env.
NO necesitas tocar este archivo.
"""

import logging
from openai import AsyncOpenAI
from config.settings import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL

logger = logging.getLogger(__name__)

# ── Cliente OpenAI-compatible (instancia global, reutilizable) ──
_client = AsyncOpenAI(
    api_key=LLM_API_KEY or "placeholder",   # placeholder hasta que llegue el key
    base_url=LLM_BASE_URL,
)


async def ask_llm(messages: list[dict]) -> str:
    """
    Envía el historial de mensajes al LLM y devuelve su respuesta.

    Args:
        messages: Lista de dicts con formato OpenAI:
                  [{"role": "system"|"user"|"assistant", "content": "..."}]

    Returns:
        Texto con la respuesta del modelo.
    """
    if not LLM_API_KEY:
        return (
            "[!] El bot aún no tiene un LLM configurado.\n"
            "Agrega tu LLM_API_KEY en el archivo .env y reiníciame."
        )

    try:
        kwargs = {
            "model": LLM_MODEL,
            "messages": messages,
        }
        
        # Si estamos usando Nemotron de NVIDIA, agregamos sus configuraciones extras
        if "nemotron" in LLM_MODEL.lower():
            kwargs["extra_body"] = {
                "chat_template_kwargs": {"enable_thinking": True},
                "reasoning_budget": 8192
            }
            kwargs["max_tokens"] = 8192
            
        response = await _client.chat.completions.create(**kwargs)
        return response.choices[0].message.content or "[!] Respuesta vacía del modelo."

    except Exception as e:
        logger.error("Error al llamar al LLM: %s", e)
        raise
