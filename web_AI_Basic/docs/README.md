# AI_Agent_Basic_Web — README

Interfaz web alternativa para el curso básico de Agentes IA (IEEE CS PUCP). Esta versión utiliza Node.js, Express y Vanilla JS para crear un entorno de chat en el navegador.

## Requisitos
- Node.js instalado en el sistema
- Una API Key válida de LLM (actualmente configurado para usar Llama 3.3 a través del endpoint de NVIDIA o compatibles).

## Instalación y Uso
1. Instalar dependencias:
```bash
npm install
```
2. Crear archivo `.env` tomando como base `.env.example`.
3. Ejecutar el servidor:
```bash
npm start
# O alternativamente: node index.js
```
4. Abrir en el navegador: `http://localhost:3000`

## Arquitectura
- `index.js`: Servidor Express en el puerto 3000. Actúa como proxy seguro hacia la API del LLM. Contiene la lógica de memoria corta conversacional.
- `public/`: Carpeta con los estáticos (HTML, CSS, JS) para la interfaz web.
- `system_prompt.txt`: Instrucciones maestras de la IA.

> **Regla estricta:** Este proyecto tiene prohibido el uso de emojis en código, respuestas y documentación. Mantenemos el estándar profesional.
