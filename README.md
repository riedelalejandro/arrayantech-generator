# arrayantech-generator

Sistema de prospección y generación de sitios web para negocios locales, potenciado por Claude Code.

## Flujo de trabajo

```
scripts/buscar-negocios.py  ← sin tokens, llama directo a Google Places API
        │
/prospectar [ciudad] [radio] [categoría]
        │
        ├── 1. Busca negocios (Python script, 0 tokens)
        ├── 2. Puntúa cada prospecto (score 0-100)
        ├── 3. Investiga en internet los HOT (score ≥ 80)
        └── 4. Genera detalles.md por cada prospecto HOT
                    │
                    └── /generar-sitio [slug] → Sitio Next.js en GitHub + Vercel
```

## Estructura

```
├── scripts/
│   ├── buscar-negocios.py     # Búsqueda via Google Places API (sin LLM)
│   └── puntuar-prospectos.py  # Pre-filtro + scoring determinístico (sin LLM)
├── prompts/
│   ├── prompt.md              # Prompt principal para generar el sitio web
│   └── detalles.md            # Template de información del negocio
├── negocios/                  # Output: carpetas por negocio prospectado
│   ├── {ciudad}-{radio}-{rubro}.md   # Resultados de búsqueda
│   └── {slug-negocio}/
│       ├── detalles.md        # Info del negocio lista para generar el sitio
│       └── web/               # Sitio Next.js generado (repo independiente)
└── .claude/
    └── skills/
        ├── prospectar/           # Orquestador del pipeline completo
        ├── buscar-negocios/      # Invoca el script Python de búsqueda
        ├── analizar-prospectos/  # Scoring de prospectos
        └── generar-sitio/        # Genera sitio, crea repo GitHub y deploya en Vercel
```

## Requisitos

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
- Python 3.9+
- Variable de entorno `GOOGLE_PLACES_API_KEY` en `.env`
- `gh` CLI autenticado (para crear repos en GitHub)
- `vercel` CLI instalado (para deployar)

## Uso

### Prospección completa

```
/prospectar Córdoba 5 restaurantes
```

Busca negocios, los puntúa, investiga los mejores y genera carpetas con `detalles.md` listas.

### Solo buscar negocios (sin gastar tokens)

Opción A — directamente con Python:
```bash
python scripts/buscar-negocios.py --ciudad "Mendoza" --radio 10 --rubro alojamiento
```

Opción B — desde Claude:
```
/buscar-negocios Mendoza 10 alojamientos
```

### Generar sitio web

Con un `detalles.md` completo en `negocios/{slug}/`:

```
/generar-sitio los-ciervos
```

Crea el repo en GitHub, genera el sitio Next.js, hace commit/push y deploya en Vercel.
Estilos disponibles: Clean SaaS (1), Dark Premium (2), Bold Editorial (3), Soft Modern (4), Brutalist Modern (5).

## Stack de los sitios generados

Next.js 15 (App Router) · Turbopack · Tailwind CSS v4 · Framer Motion · Lucide React · TypeScript · Vercel
