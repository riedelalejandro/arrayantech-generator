# AGENTS.md

## Arquitectura de agentes

El pipeline de prospección usa un patrón orquestador + subagentes:

```
/prospectar (orquestador)
    │
    ├── Fase 1: scripts/buscar-negocios.py   ← Python, 0 tokens
    │   └── Google Places API: geocoding → nearby search → place details
    │
    ├── Fase 2: scripts/puntuar-prospectos.py ← Python, 0 tokens
    │   └── Pre-filtro builder domains + scoring determinístico + ángulos de venta
    │
    └── Fase 3: Por cada HOT (score ≥ 80), 3 subagentes en paralelo:  ← LLM
        ├── Subagente CONVERSIÓN — objeciones, argumentos de venta, FAQ, precios
        ├── Subagente ATRACCIÓN  — keywords, dolores, headlines, diferenciadores
        └── Subagente RETENCIÓN  — valores del cliente, features de fidelización, tono
```

## Descripción de cada agente

### prospectar (orquestador)

- **Responsabilidad**: coordinar el pipeline completo de prospección
- **Input**: ciudad, radio (km), categoría
- **Output**: carpetas en `negocios/` con `detalles.md` por cada prospecto HOT
- **Invoca**: `/buscar-negocios`, `/analizar-prospectos`, y 3 subagentes de investigación web

### buscar-negocios

- **Responsabilidad**: invocar `scripts/buscar-negocios.py` con los parámetros recibidos
- **Implementación**: script Python standalone — **0 tokens de LLM**
- **Input**: ciudad, radio, rubro (opcional)
- **Output**: archivo `.md` en `negocios/` con tabla de resultados + JSON crudo
- **API**: Google Geocoding + Nearby Search + Place Details
- **Límites**: máximo 60 negocios (3 páginas), respeta rate limits (2s entre páginas, 1s entre requests)

### puntuar-prospectos *(script Python — reemplaza analizar-prospectos para el pipeline)*

- **Responsabilidad**: pre-filtrar y puntuar todos los negocios en batch
- **Implementación**: script Python standalone — **0 tokens de LLM**
- **Input**: archivo `.md` generado por `buscar-negocios.py`
- **Output**: `{archivo}-scored.md` con negocios ordenados por score, ángulos de venta y JSON para siguiente fase
- **Criterios de scoring** (idénticos al skill `/analizar-prospectos`):
  - Presencia digital ausente (35 pts): sin web, sin teléfono, sin reseñas
  - Atractivo del rubro (30 pts): rubros premium puntúan más
  - Validación del negocio (20 pts): rating y cantidad de reseñas
  - Facilidad de contacto (15 pts): tiene teléfono y dirección completa
- **por_qué / ángulo_venta**: generados con templates por rubro (no requiere LLM)

### analizar-prospectos *(skill LLM — usar solo fuera del pipeline automatizado)*

- **Responsabilidad**: puntuar un negocio individual de forma interactiva
- **Cuándo usar**: cuando el usuario quiere analizar un negocio suelto manualmente
- **En el pipeline**: reemplazado por `scripts/puntuar-prospectos.py`

### Subagentes de investigación (Fase 3)

Se lanzan en paralelo para cada negocio HOT. No son skills independientes, los crea el orquestador:

| Subagente | Foco | Output clave |
|-----------|------|-------------|
| CONVERSIÓN | Objeciones, prueba social, precios | `objeciones[]`, `argumentos_venta[]`, `faq[]`, `precios{}` |
| ATRACCIÓN | Keywords, dolores, propuesta de valor | `keywords[]`, `dolores[]`, `headline_sugerido`, `diferenciadores[]` |
| RETENCIÓN | Fidelización, tono, métricas | `valores_clientes[]`, `features_retencion[]`, `tono_sugerido`, `metricas[]` |

## Manejo de errores

- Si un subagente de scoring falla → se saltea el negocio
- Si un subagente de investigación falla → se continúa con los otros 2, secciones afectadas se marcan `[PENDIENTE]`
- Si ningún negocio llega a HOT → se reportan los scores y se sugiere ampliar radio o cambiar categoría
