# Meta Llama 3.3 (70B Instruct)

Información técnica y características del modelo usado como motor del agente web.

## Resumen del Modelo

| Característica | Detalle |
|---|---|
| **Arquitectura** | Llama 3.3 (Auto-regresivo, optimizado, Grouped-Query Attention - GQA) |
| **Parámetros** | 70 billones (70B) |
| **Longitud de Contexto** | 128,000 (128k) tokens |
| **Datos de Entrada/Salida** | Texto multilingüe (Entrada) / Texto y código multilingüe (Salida) |
| **Idiomas Soportados** | Inglés, Alemán, Francés, Italiano, Portugués, Hindi, Español y Tailandés |
| **Mejor uso para** | Casos de uso de diálogo multilingüe, tareas de razonamiento y asistencia. |
| **Licencia** | Llama 3.3 Community License Agreement (Apto para uso comercial) |
| **Desarrollador** | Meta |
| **Datos Totales (Pretraining)** | Más de 15 Trillones de tokens |
| **Corte de Datos** | Diciembre de 2023 (Pretraining) |
| **Fecha de Lanzamiento (70B)**| 6 de Diciembre de 2024 |

---

## Entrenamiento y Optimización

- **SFT y RLHF:** Las versiones afinadas ("tuned") utilizan aprendizaje supervisado (SFT) y aprendizaje reforzado con feedback humano (RLHF) para alinearlo hacia la utilidad y la seguridad humana.
- **Datos de Afinamiento (Tuning):** Incluye datos de instrucciones generadas por humanos públicos e internos, así como más de 25 millones de ejemplos generados sintéticamente.
- **Impacto Ambiental:** El entrenamiento tomó ~39.3 millones de horas de GPU H100 (700W), con cero emisiones reales basadas en mercado debido al uso de energía 100% renovable en los centros de Meta.

## Nuevas Capacidades vs Generaciones Previas
1. **Multilingüismo Nativo:** Soporte oficial para 8 idiomas, logrando puntajes altísimos en la métrica MGSM (91.1).
2. **Contexto Extenso:** Almacena hasta 128k tokens (equivalente a cientos de páginas de texto).
3. **Uso de Herramientas (Tool-Use):** Entrenado específicamente para integrarse y comunicarse con sistemas e invocar funciones de software.
4. **Mejoras en Codificación y Matemáticas:** Elevó significativamente los puntajes frente a Llama 3.1 8B y Llama 3.1 70B (HumanEval pass@1 subió a 88.4, y el Math CoT subió de 68.0 a 77.0).

## Seguridad y Despliegue Responsable
Meta provee diversas herramientas en capas (Prompt Guard, Code Shield y Llama Guard 3) que los desarrolladores deben aplicar para asegurar que el contenido ofensivo, dañino o relacionado con tácticas de seguridad avanzadas sea mitigado adecuadamente en el despliegue final.
