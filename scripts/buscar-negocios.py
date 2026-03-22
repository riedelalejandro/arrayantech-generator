#!/usr/bin/env python3
"""
Búsqueda de negocios locales via Google Places API.

Uso:
    python scripts/buscar-negocios.py --ciudad "San Martín de los Andes" --radio 5 --rubro restaurant
    python scripts/buscar-negocios.py --ciudad "Bariloche" --radio 10
    python scripts/buscar-negocios.py --ciudad "Mendoza" --radio 3 --rubro hotel --api-key TU_KEY

    # Múltiples rubros (supera el límite de 60 con deduplicación automática):
    python scripts/buscar-negocios.py --ciudad "Potrerillos" --radio 5 --rubros "restaurant,lodging,campground"

La API key se lee en este orden:
  1. --api-key argumento
  2. Variable de entorno GOOGLE_PLACES_API_KEY
  3. Archivo .env en la raíz del proyecto

Salida:
    negocios/{ciudad}-{radio}[-{rubro}|multi].md  con tablas + bloque JSON para el pipeline
"""

import argparse
import json
import os
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_dotenv(path: Path) -> None:
    """Lee .env sin dependencias externas."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def slugify(text: str) -> str:
    """Convierte texto en slug: minúsculas, sin tildes, sin espacios."""
    nfkd = unicodedata.normalize("NFKD", text)
    ascii_str = nfkd.encode("ascii", "ignore").decode("ascii")
    slug = ascii_str.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug


def get(url: str, params: dict) -> dict:
    """GET JSON con urllib (sin dependencias externas)."""
    full_url = url + "?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(full_url, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  ⚠ Error HTTP: {e}", file=sys.stderr)
        return {}


# ---------------------------------------------------------------------------
# Google Places API
# ---------------------------------------------------------------------------

BASE_GEO = "https://maps.googleapis.com/maps/api/geocode/json"
BASE_NEARBY = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
BASE_DETAILS = "https://maps.googleapis.com/maps/api/place/details/json"


def geocode(city: str, api_key: str) -> tuple[float, float]:
    data = get(BASE_GEO, {"address": city, "key": api_key})
    if data.get("status") != "OK":
        raise SystemExit(f"❌ Geocoding falló para '{city}': {data.get('status')} — {data.get('error_message', '')}")
    loc = data["results"][0]["geometry"]["location"]
    return loc["lat"], loc["lng"]


def nearby_search_one(lat: float, lng: float, radius_m: int, place_type: str, api_key: str) -> list[str]:
    """Devuelve lista de place_ids para un rubro (máx 60, 3 páginas)."""
    place_ids = []
    params = {
        "location": f"{lat},{lng}",
        "radius": radius_m,
        "language": "es",
        "key": api_key,
    }
    if place_type:
        params["type"] = place_type

    page = 0
    next_token = None

    while page < 3:
        if next_token:
            time.sleep(2)  # Google requiere esperar antes de usar next_page_token
            params = {"pagetoken": next_token, "key": api_key}

        data = get(BASE_NEARBY, params)
        status = data.get("status")

        if status not in ("OK", "ZERO_RESULTS"):
            print(f"  ⚠ Nearby search status: {status}", file=sys.stderr)
            break

        for r in data.get("results", []):
            pid = r.get("place_id")
            if pid:
                place_ids.append(pid)

        next_token = data.get("next_page_token")
        if not next_token:
            break
        page += 1

    return place_ids


def nearby_search(lat: float, lng: float, radius_m: int, rubros: list[str], api_key: str) -> list[str]:
    """Busca múltiples rubros y devuelve place_ids deduplicados."""
    seen = set()
    result = []

    search_list = rubros if rubros else [""]
    for rubro in search_list:
        label = f"'{rubro}'" if rubro else "general"
        print(f"  🔎 Buscando rubro {label}...", end=" ", flush=True)
        ids = nearby_search_one(lat, lng, radius_m, rubro, api_key)
        nuevos = [pid for pid in ids if pid not in seen]
        seen.update(nuevos)
        result.extend(nuevos)
        print(f"{len(ids)} encontrados, {len(nuevos)} nuevos (total acumulado: {len(result)})")

    return result


DETAIL_FIELDS = (
    "place_id,name,formatted_address,formatted_phone_number,"
    "international_phone_number,website,rating,user_ratings_total,"
    "business_status,types"
)


def get_details(place_id: str, api_key: str) -> Optional[dict]:
    data = get(BASE_DETAILS, {
        "place_id": place_id,
        "fields": DETAIL_FIELDS,
        "language": "es",
        "key": api_key,
    })
    if data.get("status") != "OK":
        return None

    r = data.get("result", {})
    if r.get("business_status") == "CLOSED_PERMANENTLY":
        return None

    website = r.get("website") or None
    return {
        "nombre": r.get("name", ""),
        "dirección": r.get("formatted_address", ""),
        "teléfono": r.get("formatted_phone_number") or r.get("international_phone_number") or None,
        "sitio_web": website,
        "tiene_web": bool(website),
        "rating": r.get("rating", 0) or 0,
        "cantidad_reseñas": r.get("user_ratings_total", 0) or 0,
        "estado": r.get("business_status", "UNKNOWN"),
        "categorías": (r.get("types") or [])[:3],
    }


# ---------------------------------------------------------------------------
# Markdown output
# ---------------------------------------------------------------------------

def build_markdown(city: str, radius_km: int, rubro: str, negocios: list[dict]) -> str:
    sin_web = [n for n in negocios if not n["tiene_web"]]
    con_web = [n for n in negocios if n["tiene_web"]]
    total = len(negocios)
    pct_sin = round(len(sin_web) / total * 100) if total else 0
    pct_con = round(len(con_web) / total * 100) if total else 0
    hoy = date.today().isoformat()

    lines = [
        f"# Negocios en {city}",
        "",
        f"**Búsqueda realizada:** {hoy}",
        f"**Radio:** {radius_km} km",
        f"**Rubro:** {rubro or 'General'}",
        f"**Total encontrados:** {total}",
        f"**Con sitio web:** {len(con_web)} ({pct_con}%)",
        f"**Sin sitio web:** {len(sin_web)} ({pct_sin}%)",
        "",
        "---",
        "",
        f"## Sin sitio web ({len(sin_web)})",
        "",
        "> Prospectos principales para venta de sitios web.",
        "",
        "| # | Nombre | Dirección | Teléfono | Rating | Reseñas | Categorías |",
        "|---|--------|-----------|----------|--------|---------|------------|",
    ]

    for i, n in enumerate(sin_web, 1):
        cats = ", ".join(n["categorías"])
        tel = n["teléfono"] or "—"
        lines.append(
            f"| {i} | {n['nombre']} | {n['dirección']} | {tel} "
            f"| {n['rating']} | {n['cantidad_reseñas']} | {cats} |"
        )

    lines += [
        "",
        "---",
        "",
        f"## Con sitio web ({len(con_web)})",
        "",
        "| # | Nombre | Sitio Web | Dirección | Teléfono | Rating | Reseñas |",
        "|---|--------|-----------|-----------|----------|--------|---------|",
    ]

    for i, n in enumerate(con_web, 1):
        tel = n["teléfono"] or "—"
        web = n["sitio_web"] or "—"
        lines.append(
            f"| {i} | {n['nombre']} | {web} | {n['dirección']} | {tel} "
            f"| {n['rating']} | {n['cantidad_reseñas']} |"
        )

    lines += [
        "",
        "---",
        "",
        "## Datos crudos (JSON)",
        "",
        "> Para uso del skill /analizar-prospectos. No editar manualmente.",
        "",
        "```json",
        json.dumps(negocios, ensure_ascii=False, indent=2),
        "```",
        "",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Busca negocios locales con Google Places API y genera un .md de prospectos."
    )
    parser.add_argument("--ciudad", required=True, help="Nombre de la ciudad")
    parser.add_argument("--radio", type=int, default=5, help="Radio en km (default: 5)")
    parser.add_argument("--rubro", default="", help="Tipo de negocio (ej: restaurant, hotel). Opcional.")
    parser.add_argument("--rubros", default="", help="Múltiples rubros separados por coma (ej: restaurant,cafe,bar). Supera el límite de 60.")
    parser.add_argument("--api-key", default="", help="Google Places API Key. Si se omite, lee de .env")
    parser.add_argument("--output-dir", default="negocios", help="Carpeta de salida (default: negocios/)")
    args = parser.parse_args()

    # Cargar .env desde la raíz del proyecto (un nivel arriba de scripts/)
    project_root = Path(__file__).parent.parent
    load_dotenv(project_root / ".env")

    api_key = args.api_key or os.environ.get("GOOGLE_PLACES_API_KEY", "")
    if not api_key:
        raise SystemExit(
            "❌ Falta la API Key de Google Places.\n"
            "   Opciones:\n"
            "     1. Pasarla con --api-key TU_KEY\n"
            "     2. Definir GOOGLE_PLACES_API_KEY en el archivo .env\n"
            "     3. Exportar: export GOOGLE_PLACES_API_KEY=TU_KEY"
        )

    ciudad = args.ciudad
    radio_km = args.radio
    radius_m = radio_km * 1000

    # Construir lista de rubros a buscar
    if args.rubros:
        rubros = [r.strip() for r in args.rubros.split(",") if r.strip()]
    elif args.rubro.strip():
        rubros = [args.rubro.strip()]
    else:
        rubros = []

    rubro_label = ", ".join(rubros) if rubros else "general"
    multi = len(rubros) > 1

    print(f"\n🔍 Buscando negocios en {ciudad} ({radio_km} km) — {rubro_label}...")
    if multi:
        print(f"  📦 Modo multi-rubro: {len(rubros)} búsquedas con deduplicación automática")

    # 1. Geocodificar
    print("  📍 Geocodificando ciudad...", end=" ", flush=True)
    lat, lng = geocode(ciudad, api_key)
    print(f"({lat:.4f}, {lng:.4f})")

    # 2. Nearby search (uno o múltiples rubros)
    if not multi:
        print(f"  🏪 Buscando negocios cercanos (hasta 3 páginas × 20)...", end=" ", flush=True)
    else:
        print(f"  🏪 Buscando negocios cercanos por rubro:")
    place_ids = nearby_search(lat, lng, radius_m, rubros, api_key)
    if not multi:
        print(f"{len(place_ids)} encontrados")
    else:
        print(f"  ✅ Total único: {len(place_ids)} place_ids")

    # 3. Place details
    print(f"  📋 Obteniendo detalles de {len(place_ids)} negocios...")
    negocios = []
    failed = []
    for i, pid in enumerate(place_ids, 1):
        print(f"     {i}/{len(place_ids)}...", end="\r", flush=True)
        details = get_details(pid, api_key)
        if details:
            negocios.append(details)
        else:
            failed.append(pid)
        # Respetar límite 60 RPM → ~1 req/s cuando hay muchos
        if len(place_ids) > 50:
            time.sleep(1)
    print(f"  ✅ {len(negocios)} negocios procesados ({len(failed)} saltados)         ")

    if not negocios:
        print("\n⚠ No se encontraron negocios. Probá con otro radio o rubro.")
        return

    # 4. Generar archivo
    output_dir = project_root / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    parts = [slugify(ciudad), str(radio_km)]
    if len(rubros) == 1:
        parts.append(slugify(rubros[0]))
    elif len(rubros) > 1:
        parts.append("multi")
    filename = "-".join(parts) + ".md"
    output_path = output_dir / filename

    md = build_markdown(ciudad, radio_km, rubro_label, negocios)
    output_path.write_text(md, encoding="utf-8")

    # Resumen
    sin_web = [n for n in negocios if not n["tiene_web"]]
    con_web = [n for n in negocios if n["tiene_web"]]
    total = len(negocios)

    print(f"""
✅ Búsqueda completada
📍 Ciudad: {ciudad} ({radio_km} km) — {rubro_label}
🏪 Negocios encontrados: {total}{f" (deduplicados de {len(rubros)} búsquedas)" if multi else ""}
🌐 Con sitio web:  {len(con_web)} ({round(len(con_web)/total*100) if total else 0}%)
🚫 Sin sitio web:  {len(sin_web)} ({round(len(sin_web)/total*100) if total else 0}%)
💾 Archivo guardado: {output_path.relative_to(project_root)}

👉 Para analizar los prospectos ejecutá: /prospectar (o /analizar-prospectos)
""")


if __name__ == "__main__":
    main()
