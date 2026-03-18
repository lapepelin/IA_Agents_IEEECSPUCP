import os
import logging
from typing import List, Dict
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore
from src.supabase_client import get_supabase_client

# Configuración de Logging Profesional
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("DocumentProcessor")

def process_pdf_and_store(file_path: str, original_filename: str) -> int:
    """
    Procesador de documentos de alta calidad.
    Extrae, divide, vectoriza y persiste PDFs en Supabase pgvector.
    """
    if not os.path.exists(file_path):
        logger.error(f"Archivo no encontrado: {file_path}")
        raise FileNotFoundError(f"No se pudo encontrar el archivo en {file_path}")

    try:
        logger.info(f"Procesando archivo: {original_filename}")
        
        # 1. CARGA INTELIGENTE
        # PyMuPDF es el cargador más rápido y preciso para Python
        loader = PyMuPDFLoader(file_path)
        documents = loader.load()
        logger.info(f"Cargadas {len(documents)} páginas del PDF.")

        # 2. DIVISIÓN SEMÁNTICA (Chunking)
        # Usamos RecursiveCharacterTextSplitter para mantener párrafos y oraciones juntas
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,      # Tamaño óptimo para modelos all-MiniLM
            chunk_overlap=150,   # Overlap para mantener contexto entre fragmentos
            length_function=len,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        
        chunks = text_splitter.split_documents(documents)
        logger.info(f"Documento dividido en {len(chunks)} fragmentos.")

        # 3. ENRIQUECIMIENTO DE METADATOS
        for chunk in chunks:
            chunk.metadata["source_file"] = original_filename
            # Limpiamos metadatos para asegurar compatibilidad con JSONB de Supabase
            chunk.metadata = {k: str(v) for k, v in chunk.metadata.items() if v is not None}

        # 4. GENERACIÓN DE EMBEDDINGS (Local & Gratis)
        # all-MiniLM-L6-v2 es extremadamente eficiente para CPU/Memoria
        logger.info("Generando vectores latentes (Embeddings)...")
        embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}, # Forzamos CPU para máxima compatibilidad
            encode_kwargs={'normalize_embeddings': True} # Normalización para mejor búsqueda de coseno
        )

        # 5. PERSISTENCIA VECTORIAL
        supabase = get_supabase_client()
        
        SupabaseVectorStore.from_documents(
            chunks,
            embeddings,
            client=supabase,
            table_name="documents",
            query_name="match_documents"
        )

        logger.info(f"¡Éxito! {len(chunks)} vectores persistidos en Supabase.")
        return len(chunks)

    except Exception as e:
        logger.exception(f"Falla crítica en el procesamiento del documento: {e}")
        raise
