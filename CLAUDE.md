# CLAUDE.md

## Qué es este proyecto

Generador de sitios web para negocios locales. El flujo tiene dos fases:

1. **Prospección**: buscar negocios en una ciudad, puntuar cuáles son buenos candidatos para venderles un sitio web, e investigar los mejores.
2. **Generación**: usar `prompts/prompt.md` + un `detalles.md` completado para generar un sitio Next.js production-ready.

## Archivos clave

- `prompts/prompt.md` — Prompt maestro para generar el sitio. Define stack, estructura, secciones y 5 estilos visuales.
- `prompts/detalles.md` — Template con toda la info del negocio. Es la fuente de verdad para el contenido del sitio.
- `negocios/README.md` — **Registro central de todos los prospectos y sitios en producción.** Se actualiza automáticamente al correr `/prospectar` (agrega filas) y `/generar-sitio` (mueve fila a producción con URL).
- `negocios/` — Output de la prospección. Estructura en dos niveles: `negocios/{busqueda}/{negocio}/`. Cada búsqueda tiene su propia carpeta con los `.md` del scoring y las subcarpetas de cada negocio HOT (cada una con `detalles.md` y subcarpeta `web/`).
- `scripts/buscar-negocios.py` — Búsqueda via Google Places API. No consume tokens.
- `scripts/puntuar-prospectos.py` — Pre-filtro + scoring de los 60 negocios en batch. No consume tokens.

## Skills disponibles

- `/prospectar [ciudad] [radio] [categoría]` — Pipeline completo: buscar → puntuar → investigar → generar detalles.md
- `/buscar-negocios [ciudad] [radio] [rubro]` — Invoca `scripts/buscar-negocios.py` (0 tokens de LLM)
- `/analizar-prospectos` — Recibe datos de un negocio y devuelve score + tier + ángulo de venta
- `/generar-sitio [slug]` — Crea repo GitHub, genera sitio Next.js desde detalles.md, deploya en Vercel

## Reglas importantes

- **Nunca inventar datos**. Si un campo no tiene info, marcarlo como `[PENDIENTE]`.
- La API Key de Google Places está en `.env` como `GOOGLE_PLACES_API_KEY`. Ver `.env.example` para referencia.
- La búsqueda y el scoring (`/buscar-negocios`, `/prospectar` Fase 2) corren scripts Python. Las Fases 1 y 2 del pipeline no consumen tokens.
- Los sitios generados usan: Next.js 15, Tailwind CSS v4, Framer Motion, Lucide React, TypeScript.
- Los sitios tienen 9 secciones: Hero (imagen de fondo) → Problem → Solution → Gallery → Social Proof → Pricing → FAQ → Map → Footer.
- Todo el contenido del sitio viene de `detalles.md`, nunca de lorem ipsum.
- Al generar un sitio, el usuario debe indicar el estilo visual (1-5). Si no lo indica, preguntar.
