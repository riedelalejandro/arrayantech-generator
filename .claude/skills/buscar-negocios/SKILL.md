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

Verificá si existe la variable de entorno `GOOGLE_PLACES_API_KEY`. Si no existe, pedila al usuario antes de continuar.

---

## Paso 1 — Geocodificar la ciudad

Llamá a la Geocoding API para obtener coordenadas:

```
GET https://maps.googleapis.com/maps/api/geocode/json?address={CIUDAD}&key={API_KEY}
```

Extraé `results[0].geometry.location` → `{ lat, lng }`. Si falla, reportá el error y detenete.

---

## Paso 2 — Buscar negocios (Nearby Search)

Convertí el radio de km a metros (× 1000). Llamá a Nearby Search:

```
GET https://maps.googleapis.com/maps/api/place/nearbysearch/json
  ?location={LAT},{LNG}
  &radius={RADIO_METROS}
  &type={RUBRO_SI_APLICA}
  &language=es
  &key={API_KEY}
```

Paginá con `next_page_token` hasta un máximo de **60 negocios** (3 páginas). Esperá 2 segundos entre páginas. Guardá el `place_id` de cada resultado.

---

## Paso 3 — Obtener detalles de cada negocio

Para cada `place_id`:

```
GET https://maps.googleapis.com/maps/api/place/details/json
  ?place_id={PLACE_ID}
  &fields=name,formatted_address,formatted_phone_number,international_phone_number,website,rating,user_ratings_total,business_status,types
  &language=es
  &key={API_KEY}
```

Extraé por negocio:
- `nombre`, `dirección`, `teléfono` (usar `formatted_phone_number`, null si no tiene)
- `sitio_web` (null si no tiene) → derivar `tiene_web: true/false`
- `rating` (0 si no tiene), `cantidad_reseñas` (0 si no tiene)
- `estado` (`business_status`), `categorías` (primeros 3 de `types`)

Excluí negocios con `business_status: CLOSED_PERMANENTLY`. Esperá 1s entre llamadas si hay más de 60 negocios para respetar el límite de 60 RPM.

---

## Paso 4 — Generar el archivo Markdown

Nombre del archivo: `{ciudad}-{radio}-{rubro}.md`, todo en minúsculas, sin tildes, sin espacios (guión medio). Si el rubro es "General", omitirlo del nombre.
- "Buenos Aires", 5km, restaurantes → `buenos-aires-5-restaurantes.md`
- "Córdoba", 2km, alojamientos → `cordoba-2-alojamientos.md`
- "San Martín", 10km, general → `san-martin-10.md`

Guardarlo en la carpeta `negocios/` del proyecto. Si no existe, crearla antes de guardar.

Estructura:

```markdown
# Negocios en {CIUDAD}

**Búsqueda realizada:** {FECHA_ISO}
**Radio:** {RADIO} km
**Rubro:** {RUBRO o "General"}
**Total encontrados:** {N}
**Con sitio web:** {N_CON} ({%}%)
**Sin sitio web:** {N_SIN} ({%}%)

---

## Sin sitio web ({N_SIN})

> Prospectos principales para venta de sitios web.

| # | Nombre | Dirección | Teléfono | Rating | Reseñas | Categorías |
|---|--------|-----------|----------|--------|---------|------------|
...

---

## Con sitio web ({N_CON})

| # | Nombre | Sitio Web | Dirección | Teléfono | Rating | Reseñas |
|---|--------|-----------|-----------|----------|--------|---------|
...

---

## Datos crudos (JSON)

> Para uso del skill /analizar-prospectos. No editar manualmente.

\`\`\`json
[{ "nombre": "...", "dirección": "...", "teléfono": "...", "sitio_web": "...", "tiene_web": false, "rating": 4.2, "cantidad_reseñas": 87, "estado": "OPERATIONAL", "categorías": ["restaurant"] }]
\`\`\`
```

---

## Paso 5 — Resumen final

```
✅ Búsqueda completada
📍 Ciudad: {CIUDAD} ({RADIO} km)
🏪 Negocios encontrados: {N}
🌐 Con sitio web:  {N} ({%}%)
🚫 Sin sitio web:  {N} ({%}%)
💾 Archivo guardado: negocios/{ciudad}-{radio}-{rubro}.md

👉 Para analizar los prospectos ejecutá: /analizar-prospectos {CIUDAD}
```

---

## Errores comunes

| Error | Acción |
|-------|--------|
| API Key ausente o inválida | Pedirla. Obtenerla en console.cloud.google.com |
| Ciudad no encontrada | Reportar y sugerir nombres alternativos |
| Cuota excedida | Guardar lo obtenido y avisar |
| Place Details falla en un negocio | Saltearlo, listar al final cuáles fallaron |
