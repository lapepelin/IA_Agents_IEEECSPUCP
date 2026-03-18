from openai import AsyncOpenAI
from config.settings import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL

# Usamos el cliente de OpenAI asíncrono, que es el estándar y es compatible con NVIDIA/Meta/Groq
client = AsyncOpenAI(
    api_key=LLM_API_KEY,
    base_url=LLM_BASE_URL,
)

async def ask_llm(messages: list) -> str:
    """
    Envía una lista de mensajes JSON al LLM y retorna la respuesta generada.
    """
    try:
        response = await client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            # Temperatura baja (0.2) para que sea analítico y preciso (ideal para RAG)
            temperature=0.2, 
            top_p=0.7,
            max_tokens=1024
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error en LLM: {e}")
        return "Lo siento, ha ocurrido un error al conectarme con el cerebro del LLM."
