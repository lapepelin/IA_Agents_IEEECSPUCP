import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Variables de Telegram
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

# Variables del LLM
LLM_API_KEY = os.environ.get("LLM_API_KEY")
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://integrate.api.nvidia.com/v1")
LLM_MODEL = os.environ.get("LLM_MODEL", "meta/llama-3.3-70b-instruct")

# Leer el prompt del sistema
def get_system_prompt() -> str:
    prompt_path = os.path.join(os.path.dirname(__file__), "system_prompt.txt")
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Error leyendo system_prompt.txt: {e}")
        return "You are a helpful AI assistant."
