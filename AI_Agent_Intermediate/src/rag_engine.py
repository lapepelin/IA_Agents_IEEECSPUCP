import logging
from typing import List, Optional
from langchain_huggingface import HuggingFaceEmbeddings
from src.supabase_client import get_supabase_client

logger = logging.getLogger("RAGEngine")

class RAGEngine:
    """
    Clase encargada de la recuperación de documentos (Retrieval).
    Encapsula la lógica de búsqueda por similitud.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # Inicializamos el modelo de embeddings una sola vez para ahorrar memoria
        logger.info(f"Cargando modelo de embeddings: {model_name}")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            encode_kwargs={'normalize_embeddings': True}
        )
        self.supabase = get_supabase_client()

    def get_context(self, query: str, limit: int = 4, min_similarity: float = 0.5) -> Optional[str]:
        """
        Busca los fragmentos más relevantes y devuelve un contexto formateado.
        """
        try:
            # 1. Embed de la pregunta
            query_vector = self.embeddings.embed_query(query)

            # 2. Búsqueda en Supabase vía RPC
            response = self.supabase.rpc(
                "match_documents",
                {
                    "query_embedding": query_vector,
                    "match_count": limit
                }
            ).execute()

            matches = response.data
            if not matches:
                logger.info("No se encontraron fragmentos relevantes para la consulta.")
                return None

            # 3. Filtrado y Formateo
            results = []
            for m in matches:
                # Opcional: Filtrar por puntaje de similitud
                if m.get("similarity", 0) < min_similarity:
                    continue
                    
                content = m.get("content", "").replace("\n", " ")
                meta = m.get("metadata", {})
                source = meta.get("source_file", "PDF")
                page = meta.get("page", "?")
                
                results.append(f"📦 [Doc: {source} | Pág: {page}] -> {content}")

            if not results:
                return None

            logger.info(f"Recuperados {len(results)} fragmentos relevantes.")
            return "\n\n".join(results)

        except Exception as e:
            logger.error(f"Error en la recuperación RAG: {e}")
            return None

# Singleton para evitar recargar el modelo en cada mensaje
_engine_instance = None

def get_rag_context(query: str) -> Optional[str]:
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = RAGEngine()
    return _engine_instance.get_context(query)
