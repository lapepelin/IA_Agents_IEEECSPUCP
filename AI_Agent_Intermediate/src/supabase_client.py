import os
from supabase import create_client, Client

def get_supabase_client() -> Client:
    """
    Inicializa y retorna el cliente de Supabase usando la URL
    y Service Role Key configuradas en el .env.
    """
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not key:
        raise ValueError("Las credenciales de Supabase no están configuradas en el .env. Necesitas SUPABASE_URL y SUPABASE_SERVICE_ROLE_KEY.")
        
    return create_client(url, key)
