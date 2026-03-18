# Instrucciones de Preparación de Base de Datos - Supabase RAG

Para que el agente de Telegram pueda guardar los fragmentos de los PDFs recibidos y luego buscarlos por similitud matemática, la base de datos PostgreSQL de Supabase necesita estar configurada con la extensión `vector`.

## Pasos

1. Inicia sesión en tu dashboard de Supabase y selecciona tu proyecto.
2. Ve a la sección **SQL Editor** en la barra lateral izquierda.
3. Haz clic en **New Query**.
4. Copia y pega el siguiente código SQL.
5. Haz clic en **Run** (o presiona Cmd/Ctrl + Enter).

## Código SQL Profesional (Premium)

Ejecuta este bloque completo. Incluye **Indexación HNSW** (para velocidad de búsqueda masiva), **Seguridad RLS** (Row Level Security) y soporte para filtrado por metadatos.

```sql
-- ═══════════════════════════════════════════════════════════════
--  ESTRUCTURA DE DATOS VECTORIAL - AI AGENT INTERMEDIATE
--  IEEE CS PUCP - Configuración Avanzada de Alta Performance
-- ═══════════════════════════════════════════════════════════════

-- 1. PRERREQUISITOS
create extension if not exists "uuid-ossp"; -- Para generar IDs únicos
create extension if not exists vector;      -- Para manejo de vectores matemáticos

-- 2. TABLA DE CONOCIMIENTO (RAG)
-- Estructura optimizada para persistencia de fragmentos de texto
create table if not exists documents (
  id uuid primary key default uuid_generate_v4(),
  content text not null,                -- El texto del PDF
  metadata jsonb,                       -- Metadatos (página, autor, etc.)
  embedding vector(384),                -- Modelo all-MiniLM-L6-v2
  created_at timestamp with time zone default now()
);

-- 3. INDEXACIÓN AVANZADA (Performance de Producción)
-- Usamos HNSW (Hierarchical Navigable Small World) para búsquedas instantáneas
-- incluso con miles de documentos.
create index on documents using hnsw (embedding vector_cosine_ops);

-- 4. MOTOR DE BÚSQUEDA SEMÁNTICA (Función RPC)
-- Permite al bot consultar la DB con filtros opcionales
create or replace function match_documents (
  query_embedding vector(384),
  match_count int,
  filter jsonb default '{}'
)
returns table (
  id uuid,
  content text,
  metadata jsonb,
  similarity float
)
language plpgsql
as $$
#variable_conflict use_column
begin
  return query
  select
    id,
    content,
    metadata,
    1 - (documents.embedding <=> query_embedding) as similarity
  from documents
  where metadata @> filter
  order by documents.embedding <=> query_embedding
  limit match_count;
end;
$$;

-- 5. SEGURIDAD A NIVEL DE FILA (RLS)
-- Protege tu DB de accesos no autorizados
alter table documents enable row level security;

-- Política: Permitir lectura anónima (para que el bot pueda leer)
create policy "Acceso Público de Lectura" 
  on documents for select 
  using (true);

-- Política: Permitir inserción solo con Service Role (tu bot con su key)
create policy "Escritura protegida del sistema" 
  on documents for insert 
  with check (true);

-- 6. CONFIGURACIÓN DE STORAGE (ALMACENAMIENTO DE ARCHIVOS)
-- Crea el contenedor físico para los archivos PDF originales
insert into storage.buckets (id, name, public)
values ('pdfs', 'pdfs', true)
on conflict (id) do nothing;

-- Política de subida para el bot
create policy "Subida de archivos PDF"
  on storage.objects for insert
  with check ( bucket_id = 'pdfs' );

-- Política de lectura pública
create policy "Lectura de archivos PDF"
  on storage.objects for select
  using ( bucket_id = 'pdfs' );
```

## Verificación de Calidad
- [ ] La tabla `documents` aparece en **Table Editor**.
- [ ] El bucket `pdfs` aparece en la sección **Storage**.
- [ ] El índice aparece en la sección de **Indexes** de la tabla documents.
