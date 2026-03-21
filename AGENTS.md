# AGENTS.md

## Arquitectura de agentes

El pipeline de prospección usa un patrón orquestador + subagentes:

```
/prospectar (orquestador)
    │
    ├── Fase 1: /buscar-negocios
    │   └── Llama a Google Places API (geocoding → nearby search → place details)
    │
    ├── Fase 2: /analizar-prospectos × N (en paralelo)
    │   └── Un subagente por negocio, devuelve score/tier/ángulo de venta
    │
    └── Fase 3: Por cada HOT (score ≥ 80), 3 subagentes en paralelo:
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

- **Responsabilidad**: buscar negocios en un área geográfica via Google Places API
- **Input**: ciudad, radio, rubro (opcional)
- **Output**: archivo `.md` en `negocios/` con tabla de resultados + JSON crudo
- **API**: Google Geocoding + Nearby Search + Place Details
- **Límites**: máximo 60 negocios (3 páginas), respeta rate limits

### analizar-prospectos

- **Responsabilidad**: puntuar un negocio individual como prospecto de venta de sitio web
- **Input**: datos del negocio (nombre, dirección, teléfono, sitio_web, rating, reseñas, categorías)
- **Output**: JSON con score (0-100), tier (HOT/WARM/TEPID/COLD), breakdown y ángulo de venta
- **Criterios de scoring**:
  - Presencia digital ausente (35 pts): sin web, sin teléfono, sin reseñas
  - Atractivo del rubro (30 pts): rubros premium puntúan más
  - Validación del negocio (20 pts): rating y cantidad de reseñas
  - Facilidad de contacto (15 pts): tiene teléfono y dirección completa

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
