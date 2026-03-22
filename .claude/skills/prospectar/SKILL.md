---
name: prospectar
description: Agente orquestador de prospección. Recibe ciudad, radio y categorías, busca negocios (Python script), los puntúa en batch (Python script), y para los que llegan a score ≥ 70 investiga en internet y genera un detalles.md listo para usar con el prompt de sitio web.
argument-hint: "[ciudad] [radio_km] [categoría]"
---

# Agente: Prospector Automático

## Rol

Sos un agente orquestador. Tu trabajo es coordinar subagentes para transformar una búsqueda geográfica en carpetas listas para generar sitios web de negocios locales.

---

## Input

Extraé del mensaje del usuario:
- **Ciudad** — requerido
- **Radio** — en km (default: 5)
- **Categoría** — uno o varios rubros separados por coma (default: general)

---

## Fase 1 — Búsqueda de negocios

Ejecutá el script Python directamente (no gasta tokens de LLM):

- Si hay **un solo rubro**: usá `--rubro "{CATEGORÍA}"`
- Si hay **múltiples rubros** (separados por coma): usá `--rubros "{CATEGORÍA1,CATEGORÍA2,...}"`

```bash
# Un rubro:
python3 scripts/buscar-negocios.py \
  --ciudad "{CIUDAD}" \
  --radio {RADIO} \
  --rubro "{CATEGORÍA}"

# Múltiples rubros:
python3 scripts/buscar-negocios.py \
  --ciudad "{CIUDAD}" \
  --radio {RADIO} \
  --rubros "{CATEGORÍA1,CATEGORÍA2,CATEGORÍA3}"
```

Esperá a que termine. El script imprime el resumen y guarda el archivo en `negocios/`.

El archivo generado tiene el slug `{SEARCH_SLUG}` (ej: `el-chalten-2-multi`, `potrerillos-5-food`). Reorganizá inmediatamente los archivos en una carpeta de búsqueda:

```bash
mkdir -p negocios/{SEARCH_SLUG}
mv negocios/{SEARCH_SLUG}.md negocios/{SEARCH_SLUG}/
```

Leé el archivo `negocios/{SEARCH_SLUG}/{SEARCH_SLUG}.md` y extraé la lista de negocios del bloque `## Datos crudos (JSON)`.

---

## Fase 2 — Filtro previo + Scoring

Ejecutá el script Python directamente (no gasta tokens de LLM):

```bash
python3 scripts/puntuar-prospectos.py negocios/{SEARCH_SLUG}/{SEARCH_SLUG}.md
```

El script aplica el pre-filtro de dominios builder/sociales, calcula el score (0-100) de cada candidato con la misma lógica que `/analizar-prospectos`, y genera:
- `negocios/{SEARCH_SLUG}-scored.md` — tabla ordenada por score con ángulos de venta (en `negocios/`, no en la subcarpeta)
- stdout — resumen con la lista de HOT listos para investigar

Mové el scored al mismo directorio de búsqueda:

```bash
mv negocios/{SEARCH_SLUG}-scored.md negocios/{SEARCH_SLUG}/
```

Leé el archivo `negocios/{SEARCH_SLUG}/{SEARCH_SLUG}-scored.md` y extraé del bloque `## Datos JSON (para pipeline)` la lista de negocios con `score >= 70`. Si no hay ninguno, reportalo y terminá (sugerí ampliar radio o cambiar categoría).

---

## Fase 3 — Procesamiento de prospectos seleccionados

Por cada negocio con `score ≥ 70`:

### 3a — Crear carpeta

Creá la carpeta `negocios/{SEARCH_SLUG}/[slug-nombre]/` donde `slug-nombre` es el nombre del negocio en minúsculas, sin tildes, sin espacios (guión medio).
- "Camping Los Ceibos" → `negocios/{SEARCH_SLUG}/camping-los-ceibos/`

### 3b — Investigación en paralelo

Lanzá **3 subagentes en paralelo** que investiguen el negocio en internet. **Cada subagente tiene un límite estricto de 5 consultas web** (WebFetch o WebSearch). Priorizá las fuentes más relevantes y no desperdicies llamadas en resultados dudosos.

**Subagente CONVERSIÓN:**
Límite: **máximo 5 consultas web**. Investigá en internet sobre `[nombre negocio] [ciudad] [categoría]`. Tu foco es la **conversión de visitantes en clientes**:
- ¿Qué objeciones típicas tiene alguien antes de contratar este tipo de negocio?
- ¿Qué argumentos de venta y garantías funcionan para este rubro?
- ¿Qué preguntas frecuentes aparecen en Google para este tipo de negocio en Argentina?
- ¿Qué prueba social (reseñas, testimonios, métricas) mencionan negocios similares?
- ¿Qué precios o rangos de precios maneja este rubro en la zona?
- Buscá si el negocio tiene reseñas de Google, redes sociales o menciones online y extraé citas reales si las hay.

Devolvé un JSON con: `objeciones[]`, `argumentos_venta[]`, `faq[]`, `prueba_social{}`, `precios{}`.

**Subagente ATRACCIÓN:**
Límite: **máximo 5 consultas web**. Investigá en internet sobre `[nombre negocio] [ciudad] [categoría]`. Tu foco es la **atracción de nuevos clientes**:
- ¿Qué palabras clave busca alguien en Google cuando necesita este tipo de negocio en Argentina?
- ¿Cuáles son los dolores principales del cliente ideal de este rubro?
- ¿Qué headline o propuesta de valor usan los mejores competidores?
- ¿Qué diferenciadores ofrece este negocio específico vs la competencia local (basate en sus reseñas, descripción en Google Maps, redes)?
- ¿Cuál es el perfil del cliente ideal (quién es, qué necesita, cuándo busca este servicio)?

Devolvé un JSON con: `keywords[]`, `dolores[]`, `headline_sugerido`, `subheadline_sugerido`, `diferenciadores[]`, `cliente_ideal{}`.

**Subagente RETENCIÓN:**
Límite: **máximo 5 consultas web**. Investigá en internet sobre `[nombre negocio] [ciudad] [categoría]`. Tu foco es la **retención y fidelización de clientes existentes**:
- ¿Qué valoran más los clientes frecuentes de este tipo de negocio? (buscá en reseñas de Google, foros, redes)
- ¿Qué features de un sitio web ayudan a mantener el vínculo con clientes que ya compraron (reservas online, newsletter, área de clientes, WhatsApp directo)?
- ¿Qué tono de comunicación genera más confianza y lealtad en este rubro?
- ¿Qué métricas de éxito del negocio podrían destacarse ("más de X clientes", "X años en el mercado")?
- Buscá información sobre el negocio específico: ¿cuánto tiempo lleva operando, qué dicen sus clientes frecuentes?

Devolvé un JSON con: `valores_clientes[]`, `features_retencion[]`, `tono_sugerido`, `metricas[]`, `antiguedad_estimada`.

### 3c — Generar detalles.md

Con los resultados de los 3 subagentes, completá el archivo `detalles.md` siguiendo la estructura de `/prompts/detalles.md`.

**Reglas de completado:**
- Usá datos reales del negocio (nombre, dirección, teléfono, sitio web) de la fase anterior
- El `Rubro` e `Industria` se derivan de las categorías de Google Places
- `URL` → si tiene sitio_web usarlo; si no, dejarlo como `[PENDIENTE]`
- `Headline` → usá el sugerido por el subagente ATRACCIÓN, adaptado al negocio real
- `Dolores principales` → del subagente ATRACCIÓN
- `Features` → combiná los diferenciadores reales del negocio con los features de retención
- `Testimonios` → si el subagente CONVERSIÓN encontró citas reales de reseñas, usarlas; si no, dejá los campos como `[PENDIENTE — buscar reseñas reales]`
- `Métricas` → del subagente RETENCIÓN
- `FAQ` → del subagente CONVERSIÓN, priorizá las objeciones reales detectadas
- `Precios` → del subagente CONVERSIÓN; si no se encontraron, dejar como `[A consultar]`
- `Tono de voz` → del subagente RETENCIÓN
- `Color primario` → sugerí un color apropiado para el rubro (ej: verde para salud, azul para servicios profesionales)
- `SEO → Keywords` → del subagente ATRACCIÓN
- Campos sin dato disponible → marcá como `[PENDIENTE]`, nunca inventés datos

Guardá el archivo en `negocios/{SEARCH_SLUG}/[slug-nombre]/detalles.md`.

### 3d — Actualizar negocios/README.md

Después de generar el `detalles.md`, registrá el negocio en `negocios/README.md`:

1. Leé el archivo actual `negocios/README.md`
2. Agregá una fila en la tabla **"Prospectos con detalles.md listos"** con el formato:
   ```
   | {emoji_tier} {score} | {Nombre negocio} | `{SEARCH_SLUG}/{slug}` | {Rubro} | {teléfono} | ✅ | ❌ |
   ```
   - Emoji tier: 🔥 para score ≥ 80, ♨️ para 70-79
3. Si la búsqueda generó archivos nuevos de prospección, agregá una fila en la tabla **"Archivos de prospección"**:
   ```
   | `{SEARCH_SLUG}/{SEARCH_SLUG}.md` | Búsqueda raw · {ciudad} · {radio} km · {categoría} · {N} negocios |
   | `{SEARCH_SLUG}/{SEARCH_SLUG}-scored.md` | Scoring · {N_evaluados} evaluados · {N_seleccionados} seleccionados |
   ```
   Solo agregá las filas si esos archivos no estaban ya listados.
4. Guardá el archivo actualizado.

---

## Fase 4 — Resumen final

```
✅ Prospección completada
📍 Ciudad: {CIUDAD} ({RADIO} km) — {CATEGORÍA}

📊 Negocios encontrados:    {N_TOTAL}
🚫 Con sitio propio (skip): {N_CON_SITIO}
📋 Evaluados:               {N_EVALUADOS}
🔥 HOT (score ≥ 80):        {N_HOT}
⏭️  Descartados:             {N_DESCARTADOS}

Carpetas generadas:
{Por cada HOT:}
  📁 negocios/{SEARCH_SLUG}/{slug}/ — {Nombre} ({score}/100)
     ✅ detalles.md generado

👉 Para generar el sitio de un prospecto:
   /generar-sitio {SEARCH_SLUG}/{slug}
```

---

## Manejo de errores

| Situación | Acción |
|-----------|--------|
| buscar-negocios falla | Reportar y detener |
| Un subagente de scoring falla | Saltear ese negocio, registrar el error |
| Ningún negocio llega a score ≥ 80 | Reportar cuántos había y sus scores, sugerir ampliar el radio o cambiar categoría |
| Un subagente de investigación falla | Continuar con los otros 2, marcar las secciones afectadas como `[PENDIENTE — investigación fallida]` |
| El negocio no tiene información online | Completar con lo que se tiene de Google Places y marcar resto como `[PENDIENTE]` |
