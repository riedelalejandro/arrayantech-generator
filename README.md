# arrayantech-generator

Sistema de prospección y generación de sitios web para negocios locales, potenciado por Claude Code.

## Flujo de trabajo

```
/prospectar [ciudad] [radio] [categoría]
        │
        ├── 1. Busca negocios via Google Places API
        ├── 2. Puntúa cada prospecto (score 0-100)
        ├── 3. Investiga en internet los HOT (score ≥ 80)
        └── 4. Genera detalles.md por cada prospecto HOT
                    │
                    └── prompt.md + detalles.md → Sitio Next.js listo para Vercel
```

## Estructura

```
├── prompts/
│   ├── prompt.md          # Prompt principal para generar el sitio web
│   └── detalles.md        # Template de información del negocio
├── negocios/              # Output: carpetas por negocio prospectado
│   ├── {ciudad}-{radio}-{rubro}.md   # Resultados de búsqueda
│   └── {slug-negocio}/
│       └── detalles.md    # Info del negocio lista para generar el sitio
└── .claude/
    └── skills/
        ├── prospectar/           # Orquestador del pipeline completo
        ├── buscar-negocios/      # Búsqueda via Google Places API
        └── analizar-prospectos/  # Scoring de prospectos
```

## Requisitos

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
- Variable de entorno `GOOGLE_PLACES_API_KEY`

## Uso

### Prospección completa

```
/prospectar Córdoba 5 restaurantes
```

Busca negocios, los puntúa, investiga los mejores y genera carpetas con `detalles.md` listas.

### Solo buscar negocios

```
/buscar-negocios Mendoza 10 alojamientos
```

### Generar sitio web

Desde la carpeta de un negocio con su `detalles.md` completo:

```
Usá el Estilo 2 — DARK PREMIUM
```

Estilos disponibles: Clean SaaS (1), Dark Premium (2), Bold Editorial (3), Soft Modern (4), Brutalist Modern (5).

## Stack de los sitios generados

Next.js 15 (App Router) · Turbopack · Tailwind CSS v4 · Framer Motion · Lucide React · TypeScript · Vercel
