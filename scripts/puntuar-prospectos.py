#!/usr/bin/env python3
"""
Scoring de prospectos para venta de sitios web.

Lee el archivo .md generado por buscar-negocios.py (o un JSON directo),
aplica pre-filtro + scoring determinístico, y genera un nuevo archivo
con los prospectos ordenados por score.

Uso:
    python scripts/puntuar-prospectos.py negocios/san-martin-5-restaurantes.md
    python scripts/puntuar-prospectos.py negocios/bariloche-10.md --min-score 60
    python scripts/puntuar-prospectos.py negocios/mendoza-5.md --json-output scored.json

Salida:
    negocios/{original}-scored.md   con tabla de prospectos ordenada por score
    stdout                           resumen + lista de HOT listos para investigar
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional
from datetime import date
from urllib.parse import urlparse


# ---------------------------------------------------------------------------
# Pre-filtro: plataformas builder / perfiles que no son sitio propio
# ---------------------------------------------------------------------------

BUILDER_DOMAINS = {
    # Website builders
    "wix.com", "wixsite.com",
    "blogspot.com", "blogger.com",
    "wordpress.com",
    "weebly.com",
    "webnode.com", "webnode.com.ar",
    "jimdo.com",
    "site123.me",
    "godaddysites.com",
    "mystrikingly.com",
    "strikingly.com",
    # Plataformas de booking genéricas (no sitio propio)
    "wbzak.net",
    "booking.com",
    "tripadvisor.com",
    # Redes sociales usadas como "sitio web"
    "instagram.com",
    "facebook.com",
    "linktr.ee",
    "linktree.com",
}


def is_builder_or_social(url: str) -> bool:
    """Devuelve True si la URL es una plataforma builder o red social."""
    if not url:
        return False
    try:
        parsed = urlparse(url if url.startswith("http") else "https://" + url)
        host = parsed.netloc.lower().lstrip("www.")
        # Coincidencia exacta o subdominio de un builder
        for b in BUILDER_DOMAINS:
            if host == b or host.endswith("." + b):
                return True
        return False
    except Exception:
        return False


def should_score(negocio: dict) -> tuple[bool, str]:
    """
    Devuelve (pasar, razón).
    Un negocio pasa el filtro si: no tiene web, o tiene web en builder/social.
    Se descarta si tiene dominio propio.
    """
    web = negocio.get("sitio_web")
    if not web:
        return True, "sin_web"
    if is_builder_or_social(web):
        return True, "builder"
    return False, "dominio_propio"


# ---------------------------------------------------------------------------
# Scoring — reproduce exactamente la lógica de analizar-prospectos/SKILL.md
# ---------------------------------------------------------------------------

CATEGORY_SCORES = {
    # 30 pts
    "dentist": 30, "doctor": 30, "health": 30, "physiotherapist": 30,
    "beauty_salon": 30, "spa": 30,
    # 28 pts
    "lawyer": 28, "accounting": 28, "real_estate_agency": 28, "insurance_agency": 28,
    # 25 pts
    "hotel": 25, "lodging": 25, "gym": 25, "fitness_center": 25,
    # 22 pts
    "restaurant": 22, "cafe": 22, "bar": 22, "bakery": 22,
    "car_repair": 22, "car_dealer": 22,
    # 20 pts
    "electrician": 20, "plumber": 20, "painter": 20, "contractor": 20,
    "school": 20, "tutoring": 20,
    # 18 pts
    "florist": 18, "jewelry_store": 18, "clothing_store": 18,
    "pet_store": 18, "veterinary_care": 18,
    # 15 pts
    "hardware_store": 15, "furniture_store": 15,
}

CATEGORY_LABELS = {
    "dentist": "Odontología", "doctor": "Medicina", "health": "Salud",
    "physiotherapist": "Kinesiología", "beauty_salon": "Estética", "spa": "Spa/Bienestar",
    "lawyer": "Abogacía", "accounting": "Contaduría",
    "real_estate_agency": "Inmobiliaria", "insurance_agency": "Seguros",
    "hotel": "Hotel/Alojamiento", "lodging": "Alojamiento",
    "gym": "Gimnasio", "fitness_center": "Fitness",
    "restaurant": "Restaurante", "cafe": "Cafetería", "bar": "Bar", "bakery": "Panadería",
    "car_repair": "Mecánica", "car_dealer": "Concesionaria",
    "electrician": "Electricista", "plumber": "Plomería",
    "painter": "Pintura", "contractor": "Construcción",
    "school": "Educación", "tutoring": "Clases/Tutoría",
    "florist": "Florería", "jewelry_store": "Joyería",
    "clothing_store": "Indumentaria", "pet_store": "Mascotas",
    "veterinary_care": "Veterinaria", "hardware_store": "Ferretería",
    "furniture_store": "Mueblería",
}


def score_rubro(categorias: list[str]) -> tuple[int, str]:
    """Devuelve (puntos, label) del rubro con mayor puntaje."""
    best_pts = 10
    best_label = "Negocio local"
    for cat in categorias:
        pts = CATEGORY_SCORES.get(cat, 10)
        if pts > best_pts:
            best_pts = pts
            best_label = CATEGORY_LABELS.get(cat, cat.replace("_", " ").title())
    return best_pts, best_label


def score_negocio(negocio: dict) -> dict:
    """Calcula el score completo y devuelve el breakdown."""
    web = negocio.get("sitio_web")
    telefono = negocio.get("teléfono")
    rating = negocio.get("rating") or 0
    reseñas = negocio.get("cantidad_reseñas") or 0
    direccion = negocio.get("dirección") or ""
    categorias = negocio.get("categorías") or []

    # Criterio 1 — Presencia digital ausente (35 pts)
    pts_sin_web = 20 if not web else 0
    pts_sin_tel = 10 if not telefono else 0
    pts_sin_reseñas = 5 if reseñas == 0 else 0

    # Criterio 2 — Atractivo del rubro (30 pts)
    pts_rubro, rubro_label = score_rubro(categorias)

    # Criterio 3 — Validación del negocio (20 pts)
    pts_rating = 10 if rating >= 4.0 else (5 if rating >= 3.0 else 0)
    pts_reseñas = 10 if reseñas > 20 else (5 if reseñas >= 5 else 0)

    # Criterio 4 — Facilidad de contacto (15 pts)
    pts_telefono = 10 if telefono else 0
    # Heurística: la dirección tiene número de calle si hay un dígito seguido de nombre
    pts_direccion = 5 if re.search(r"\d", direccion) else 0

    total = (
        pts_sin_web + pts_sin_tel + pts_sin_reseñas
        + pts_rubro
        + pts_rating + pts_reseñas
        + pts_telefono + pts_direccion
    )
    total = min(total, 100)

    tier = (
        "HOT" if total >= 80
        else "WARM" if total >= 60
        else "TEPID" if total >= 40
        else "COLD"
    )

    return {
        "score": total,
        "tier": tier,
        "rubro_label": rubro_label,
        "breakdown": {
            "sin_web": pts_sin_web,
            "sin_telefono": pts_sin_tel,
            "sin_reseñas": pts_sin_reseñas,
            "rubro": pts_rubro,
            "rating": pts_rating,
            "reseñas": pts_reseñas,
            "telefono": pts_telefono,
            "direccion": pts_direccion,
        },
    }


# ---------------------------------------------------------------------------
# Templates de por_qué y ángulo de venta
# ---------------------------------------------------------------------------

def build_por_que(negocio: dict, scored: dict, filter_reason: str) -> str:
    """Genera la frase explicativa del score (1-2 oraciones)."""
    rating = negocio.get("rating") or 0
    reseñas = negocio.get("cantidad_reseñas") or 0
    web = negocio.get("sitio_web") or ""
    rubro = scored["rubro_label"]
    parts = []

    if filter_reason == "sin_web":
        parts.append("No tiene sitio web propio.")
    elif filter_reason == "builder":
        dominio = urlparse(web if web.startswith("http") else "https://" + web).netloc.lstrip("www.")
        parts.append(f"Su web está en {dominio} — no un sitio profesional propio.")

    if reseñas > 50:
        parts.append(f"Con {reseñas} reseñas y {rating}★ tiene demanda comprobada pero no la capitaliza online.")
    elif reseñas > 10:
        parts.append(f"Tiene {reseñas} reseñas con {rating}★ — clientes reales que no pueden referenciarlo por web.")
    elif reseñas > 0:
        parts.append(f"Está empezando a generar reseñas ({reseñas}, {rating}★) — buen momento para instalar presencia digital.")
    else:
        parts.append(f"Sin reseñas aún — el rubro {rubro} tiene alta demanda de sitios en la zona.")

    return " ".join(parts)


ANGULOS_POR_RUBRO = {
    # Salud
    "Odontología": "Tus pacientes no pueden recomendarte con un link — un sitio con turnos online y galería de tratamientos convierte búsquedas de Google en consultas directas.",
    "Medicina": "Los pacientes buscan médicos en Google antes de llamar — un sitio profesional con formulario de turnos te pone primero en la lista.",
    "Salud": "La confianza en salud se construye online antes de la primera visita — un sitio con credenciales, servicios y contacto directo es tu mejor carta de presentación.",
    "Kinesiología": "Pacientes con dolor buscan kinesiología en Google a cualquier hora — un sitio con descripción de tratamientos y reserva online captura los que no pueden esperar.",
    "Estética": "Las clientas comparan fotos y precios antes de reservar — un sitio con galería de antes/después y reserva online es tu vitrina permanente.",
    "Spa/Bienestar": "El turismo de bienestar busca opciones online desde el hotel — un sitio con servicios, precios y reserva directa captura ese tráfico antes que la competencia.",
    # Profesionales
    "Abogacía": "Los clientes buscan abogados cuando tienen urgencias — un sitio profesional con especialidades y formulario de consulta te posiciona para esa búsqueda crítica.",
    "Contaduría": "Las PYMEs cambian de contador por recomendación o Google — un sitio con servicios claros y casos de éxito genera confianza antes del primer contacto.",
    "Inmobiliaria": "Los compradores buscan propiedades online semanas antes de llamar — un sitio con catálogo y filtros los atrae mucho antes que el competidor.",
    "Seguros": "Las personas comparan precios de seguros en Google — un sitio con cotizador o formulario de contacto captura leads que hoy van a la competencia.",
    # Alojamiento
    "Hotel/Alojamiento": "Con {N} reseñas en Google, los viajeros ya te buscan — un sitio con galería, tarifas y reserva directa evita el 15% de comisión de las OTAs.",
    "Alojamiento": "Los turistas buscan alojamiento desde sus casas — un sitio con fotos, disponibilidad y reserva directa capta reservas sin intermediarios.",
    # Fitness
    "Gimnasio": "Las personas empiezan a buscar gimnasio en enero y en marzo — un sitio con precios, horarios y 'primer mes gratis' convierte esa búsqueda en inscripciones.",
    "Fitness": "Los nuevos clientes comparan opciones online antes de pisar el lugar — un sitio con servicios, testimonios y oferta de prueba cierra antes de la visita.",
    # Gastronomía
    "Restaurante": "Los turistas eligen dónde cenar desde el hotel buscando en Google — un sitio con menú, fotos y reserva online es el primer filtro que ganan o pierden.",
    "Cafetería": "Las personas eligen cafeterías por foto antes de entrar — un sitio con galería, especialidades y ubicación captura el tráfico peatonal que hoy pasa de largo.",
    "Bar": "La gente busca bares para la noche antes de salir — un sitio con propuesta, horarios y reservas te pone en la consideración antes de que elijan otro.",
    "Panadería": "Los vecinos nuevos buscan panaderías en Google Maps — un sitio con productos, horarios y pedidos online te convierte en su panadería de cabecera.",
    # Mecánica
    "Mecánica": "Los conductores con el auto roto buscan mecánica de urgencia en Google — un sitio con servicios, disponibilidad y teléfono directo captura esa demanda crítica.",
    "Concesionaria": "Los compradores de autos investigan online semanas antes de pisar un concesionario — un sitio con stock, fotos y financiación los atrae antes.",
    # Oficios
    "Electricista": "Cuando hay un problema eléctrico, la búsqueda es inmediata — un sitio con zona de cobertura, servicios y WhatsApp directo gana esa urgencia.",
    "Plomería": "Las emergencias de plomería se resuelven con el primer resultado de Google — un sitio con disponibilidad y contacto instantáneo captura esa urgencia.",
    "Pintura": "Los propietarios buscan pintores con fotos de trabajos anteriores — un galería de obras, presupuesto online y testimonios genera consultas sin salir a vender.",
    "Construcción": "Los proyectos de construcción empiezan con investigación online — un sitio con portfolio, especialidades y formulario de presupuesto atrae a quienes ya decidieron.",
    # Educación
    "Educación": "Los padres buscan colegios e institutos online antes de llamar — un sitio con propuesta pedagógica, fotos y formulario de inscripción es el primer filtro.",
    "Clases/Tutoría": "Los alumnos y padres buscan clases particulares en Google — un sitio con materias, metodología y primer contacto gratis captura esa demanda.",
    # Comercios
    "Florería": "Las flores se compran para fechas especiales — un sitio con catálogo, precios y pedidos online captura a quienes planifican con anticipación.",
    "Joyería": "Las compras de joyería son emocionales pero se investigan online — un sitio con catálogo y WhatsApp directo convierte esa búsqueda en venta.",
    "Indumentaria": "La ropa se busca en Instagram y Google juntos — un sitio con catálogo, talles y WhatsApp conecta ambos canales en una sola experiencia.",
    "Mascotas": "Los dueños de mascotas buscan productos y servicios específicos online — un sitio con catálogo y recomendaciones genera confianza y fidelización.",
    "Veterinaria": "Las mascotas con urgencias terminan en la veterinaria que aparece primero en Google — un sitio con servicios, horarios y teléfono directo gana esa búsqueda.",
    "Ferretería": "Los proyectos de casa empiezan con búsquedas en Google — un sitio con productos, marcas y consulta fácil atrae a quienes no saben dónde ir.",
    "Mueblería": "Los compradores de muebles navegan online semanas antes de comprar — un sitio con catálogo, ambientaciones y presupuesto online cierra ventas antes de la visita.",
}

DEFAULT_ANGULO = (
    "Tus clientes buscan negocios como el tuyo en Google antes de ir — "
    "un sitio profesional con contacto directo y propuesta clara es el primer paso para capturar esa demanda."
)


def build_angulo_venta(negocio: dict, scored: dict) -> str:
    """Genera el ángulo de venta personalizado según rubro y situación."""
    rubro = scored["rubro_label"]
    reseñas = negocio.get("cantidad_reseñas") or 0
    angulo = ANGULOS_POR_RUBRO.get(rubro, DEFAULT_ANGULO)
    # Sustituir {N} si aparece en el template
    return angulo.replace("{N}", str(reseñas))


# ---------------------------------------------------------------------------
# Parser del archivo .md de buscar-negocios
# ---------------------------------------------------------------------------

def parse_md_json(md_path: Path) -> list[dict]:
    """Extrae el bloque JSON del archivo .md generado por buscar-negocios.py."""
    text = md_path.read_text(encoding="utf-8")
    match = re.search(r"```json\s*\n(.*?)\n```", text, re.DOTALL)
    if not match:
        raise SystemExit(f"❌ No se encontró bloque JSON en {md_path}")
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError as e:
        raise SystemExit(f"❌ Error parseando JSON en {md_path}: {e}")


# ---------------------------------------------------------------------------
# Markdown output
# ---------------------------------------------------------------------------

TIER_EMOJI = {"HOT": "🔥", "WARM": "♨️", "TEPID": "🌡️", "COLD": "❄️"}


def build_scored_md(
    negocios_scored: list[dict],
    descartados: list[dict],
    ciudad_info: str,
) -> str:
    hot = [n for n in negocios_scored if n["tier"] == "HOT"]
    warm = [n for n in negocios_scored if n["tier"] == "WARM"]
    tepid = [n for n in negocios_scored if n["tier"] == "TEPID"]
    cold = [n for n in negocios_scored if n["tier"] == "COLD"]

    lines = [
        f"# Prospectos puntuados — {ciudad_info}",
        "",
        f"**Puntuados:** {date.today().isoformat()}",
        f"**Total evaluados:** {len(negocios_scored)}",
        f"**Descartados (dominio propio):** {len(descartados)}",
        f"**🔥 HOT (≥80):** {len(hot)}",
        f"**♨️ WARM (60–79):** {len(warm)}",
        f"**🌡️ TEPID (40–59):** {len(tepid)}",
        f"**❄️ COLD (<40):** {len(cold)}",
        "",
        "---",
    ]

    for tier_name, grupo in [("HOT", hot), ("WARM", warm), ("TEPID", tepid), ("COLD", cold)]:
        if not grupo:
            continue
        emoji = TIER_EMOJI[tier_name]
        lines += [
            "",
            f"## {emoji} {tier_name} ({len(grupo)})",
            "",
            "| Score | Nombre | Rubro | Rating | Reseñas | Web | Por qué |",
            "|-------|--------|-------|--------|---------|-----|---------|",
        ]
        for n in grupo:
            web_status = "❌ Sin web" if not n["sitio_web"] else f"⚠️ Builder"
            por_que = n.get("por_que") or ""
            lines.append(
                f"| **{n['score']}** | {n['nombre']} | {n['rubro_label']} "
                f"| {n['rating']}★ | {n['cantidad_reseñas']} | {web_status} | {por_que} |"
            )

    if hot or warm:
        lines += [
            "",
            "---",
            "",
            "## Ángulos de venta (HOT + WARM)",
            "",
        ]
        for n in hot + warm:
            angulo = n.get("angulo_venta") or ""
            lines += [
                f"### {TIER_EMOJI[n['tier']]} {n['nombre']} ({n['score']}/100)",
                f"> {angulo}",
                "",
            ]

    if descartados:
        lines += [
            "---",
            "",
            f"## Descartados — ya tienen sitio propio ({len(descartados)})",
            "",
            "| Nombre | Sitio Web | Rating | Reseñas |",
            "|--------|-----------|--------|---------|",
        ]
        for n in descartados:
            lines.append(
                f"| {n['nombre']} | {n.get('sitio_web', '—')} "
                f"| {n.get('rating', 0)}★ | {n.get('cantidad_reseñas', 0)} |"
            )

    lines += [
        "",
        "---",
        "",
        "## Datos JSON (para pipeline)",
        "",
        "> Bloque usado por /prospectar para la fase de investigación.",
        "",
        "```json",
        json.dumps(
            [
                {**n, "por_que": n.get("por_que"), "angulo_venta": n.get("angulo_venta")}
                for n in negocios_scored
            ],
            ensure_ascii=False,
            indent=2,
        ),
        "```",
        "",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Filtra y puntúa prospectos del archivo .md de buscar-negocios."
    )
    parser.add_argument(
        "input",
        help="Ruta al archivo .md de buscar-negocios (ej: negocios/bariloche-5.md)",
    )
    parser.add_argument(
        "--min-score",
        type=int,
        default=70,
        help="Score mínimo para incluir en el output (default: 70)",
    )
    parser.add_argument(
        "--json-output",
        default="",
        help="Guardar también un JSON con los resultados (opcional)",
    )
    parser.add_argument(
        "--only-hot",
        action="store_true",
        help="Imprimir solo los HOT en stdout (útil para scripts)",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"❌ Archivo no encontrado: {input_path}")

    print(f"\n📋 Leyendo {input_path.name}...", flush=True)
    negocios = parse_md_json(input_path)
    print(f"   {len(negocios)} negocios cargados.")

    # Pre-filtro
    print("🔍 Aplicando pre-filtro...", flush=True)
    candidatos = []
    descartados = []
    for n in negocios:
        pasa, razon = should_score(n)
        if pasa:
            candidatos.append((n, razon))
        else:
            descartados.append(n)

    print(f"   ✅ Candidatos: {len(candidatos)}  |  ❌ Con sitio propio: {len(descartados)}")

    # Scoring
    print(f"📊 Puntuando {len(candidatos)} candidatos...", flush=True)
    resultados = []
    for n, filter_reason in candidatos:
        scored = score_negocio(n)
        tier = scored["tier"]

        # por_que y angulo_venta solo para HOT y WARM
        por_que = None
        angulo_venta = None
        if tier in ("HOT", "WARM"):
            por_que = build_por_que(n, scored, filter_reason)
            angulo_venta = build_angulo_venta(n, scored)

        resultados.append({
            **n,
            "filter_reason": filter_reason,
            "score": scored["score"],
            "tier": tier,
            "rubro_label": scored["rubro_label"],
            "breakdown": scored["breakdown"],
            "por_que": por_que,
            "angulo_venta": angulo_venta,
        })

    # Ordenar por score descendente
    resultados.sort(key=lambda x: x["score"], reverse=True)

    # Aplicar min-score
    if args.min_score > 0:
        resultados = [r for r in resultados if r["score"] >= args.min_score]

    # Guardar .md
    stem = input_path.stem
    ciudad_info = stem.replace("-", " ").title()
    output_path = input_path.parent / f"{stem}-scored.md"
    md = build_scored_md(resultados, descartados, ciudad_info)
    output_path.write_text(md, encoding="utf-8")

    # JSON opcional
    if args.json_output:
        Path(args.json_output).write_text(
            json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"   💾 JSON guardado: {args.json_output}")

    # Resumen
    hot = [r for r in resultados if r["tier"] == "HOT"]
    warm = [r for r in resultados if r["tier"] == "WARM"]
    tepid = [r for r in resultados if r["tier"] == "TEPID"]
    cold = [r for r in resultados if r["tier"] == "COLD"]

    n_evaluados = len(candidatos)
    n_seleccionados = len(resultados)
    print(f"""
✅ Puntuación completada
📊 Evaluados:     {n_evaluados}  |  Descartados (sitio propio): {len(descartados)}
✅ Seleccionados (score ≥ {args.min_score}): {n_seleccionados}
🔥 HOT  (≥80): {len(hot)}
♨️  WARM (60–79): {len(warm)}
🌡️  TEPID(40–59): {len(tepid)}
❄️  COLD (<40):  {len(cold)}
💾 Archivo:    {output_path}
""")

    if hot:
        print("🔥 Prospectos HOT listos para investigar:")
        for n in hot:
            print(f"   [{n['score']}/100] {n['nombre']} — {n['rubro_label']}")
            if n.get("angulo_venta"):
                print(f"           → {n['angulo_venta'][:90]}...")
        print()

    if args.only_hot:
        # Salida limpia para consumo desde otro script
        print(json.dumps(hot, ensure_ascii=False))


if __name__ == "__main__":
    main()
