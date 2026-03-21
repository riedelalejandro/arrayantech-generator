# CLAUDE.md

## Qué es este proyecto

Generador de sitios web para negocios locales. El flujo tiene dos fases:

1. **Prospección**: buscar negocios en una ciudad, puntuar cuáles son buenos candidatos para venderles un sitio web, e investigar los mejores.
2. **Generación**: usar `prompts/prompt.md` + un `detalles.md` completado para generar un sitio Next.js production-ready.

## Archivos clave

- `prompts/prompt.md` — Prompt maestro para generar el sitio. Define stack, estructura, secciones y 5 estilos visuales.
- `prompts/detalles.md` — Template con toda la info del negocio. Es la fuente de verdad para el contenido del sitio.
- `negocios/` — Output de la prospección. Cada negocio HOT tiene su carpeta con `detalles.md`.

## Skills disponibles

- `/prospectar [ciudad] [radio] [categoría]` — Pipeline completo: buscar → puntuar → investigar → generar detalles.md
- `/buscar-negocios [ciudad] [radio] [rubro]` — Solo buscar negocios via Google Places API
- `/analizar-prospectos` — Recibe datos de un negocio y devuelve score + tier + ángulo de venta

## Reglas importantes

- **Nunca inventar datos**. Si un campo no tiene info, marcarlo como `[PENDIENTE]`.
- La API Key de Google Places está en `.env` como `GOOGLE_PLACES_API_KEY`. Ver `.env.example` para referencia.
- Los sitios generados usan: Next.js 15, Tailwind CSS v4, Framer Motion, Lucide React, TypeScript.
- Todo el contenido del sitio viene de `detalles.md`, nunca de lorem ipsum.
- Al generar un sitio, el usuario debe indicar el estilo visual (1-5). Si no lo indica, preguntar.
