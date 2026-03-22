---
name: buscar-negocios
description: Busca negocios locales en una ciudad usando Google Places API, identifica cuáles tienen sitio web y cuáles no, y guarda los resultados en un archivo .md con el nombre de la ciudad. Usar cuando el usuario quiera prospectar negocios o buscar clientes potenciales para venta de sitios web.
argument-hint: "[ciudad] [radio_km] [rubro_opcional]"
---

# Skill: Búsqueda de Negocios por Ciudad — Google Places API

## Input

Extraé del mensaje del usuario:
- **Ciudad** — nombre de la ciudad (requerido)
- **Radio** — en km (requerido, default: 5)
- **Rubro** — tipo de negocio a buscar (opcional, default: búsqueda general)

Si el usuario no proveyó algún dato requerido, preguntale antes de continuar.

---

## Ejecución

Esta skill delega toda la búsqueda al script Python `scripts/buscar-negocios.py`, que llama directamente a la Google Places API sin gastar tokens de LLM.

Construí el comando con los parámetros extraídos y ejecutalo:

```bash
python scripts/buscar-negocios.py \
  --ciudad "{CIUDAD}" \
  --radio {RADIO} \
  [--rubro "{RUBRO}"] \
  [--rubros "{RUBRO1},{RUBRO2},{RUBRO3}"]
```

- La API key se lee automáticamente del archivo `.env` (`GOOGLE_PLACES_API_KEY`).
- Si `.env` no existe o la key no está, el script lo reportará con instrucciones claras.
- El archivo de salida se guarda en `negocios/` con el nombre `{ciudad}-{radio}[-{rubro}|multi].md`.
- **`--rubros`** corre una búsqueda por rubro y deduplica los resultados — permite superar el límite de 60 de la API.

### Ejemplos de comando

```bash
# Solo ciudad y radio (búsqueda general)
python scripts/buscar-negocios.py --ciudad "San Martín de los Andes" --radio 5

# Un rubro
python scripts/buscar-negocios.py --ciudad "Bariloche" --radio 10 --rubro restaurant

# Múltiples rubros — supera el límite de 60
python scripts/buscar-negocios.py --ciudad "Potrerillos" --radio 5 --rubros "restaurant,lodging,campground"

# Con API key explícita (si no hay .env)
python scripts/buscar-negocios.py --ciudad "Mendoza" --radio 3 --rubro hotel --api-key TU_KEY
```

### Rubros comunes de Google Places

| Categoría | Tipos útiles |
|-----------|-------------|
| Gastronomía | `restaurant`, `cafe`, `bar`, `bakery`, `meal_delivery` |
| Alojamiento | `lodging`, `campground` |
| Salud | `pharmacy`, `doctor`, `dentist`, `gym` |
| Comercio | `store`, `supermarket`, `clothing_store`, `beauty_salon` |
| Servicios | `car_repair`, `laundry`, `bank` |

---

## Después de ejecutar

1. Mostrá al usuario el output del script (resumen de negocios encontrados + ruta del archivo).
2. Si el script falló (API key ausente, ciudad no encontrada, etc.), reportá el error y guiá al usuario.
3. Si el script terminó exitosamente, informá que puede continuar con `/prospectar` para scoring y generación de `detalles.md`.

---

## Errores comunes

| Error | Acción |
|-------|--------|
| `GOOGLE_PLACES_API_KEY` ausente | Pedirla. Obtenerla en console.cloud.google.com |
| Ciudad no encontrada | Sugerir nombres alternativos o usar nombre completo |
| Cuota excedida | El script guarda lo obtenido antes del error |
| Python no instalado | `python3 --version` para verificar; instalar si falta |
