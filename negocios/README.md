# Prospectos — Pipeline de Sitios

> Registro de todos los negocios prospectados. Actualizar manualmente cuando se genere o deploya un sitio.

---

## Leyenda de estado

| Símbolo | Significado |
|---------|-------------|
| ✅ | Completo |
| 🔄 | En proceso |
| ❌ | Pendiente |

---

## Sitios en producción

| Negocio | Ruta | Rubro | Ciudad | detalles.md | Sitio | URL |
|---------|------|-------|--------|:-----------:|:-----:|-----|
| Apart Los Ciervos | `cerro-otto-bariloche-1-alojamientos/los-ciervos` | Alojamiento | Bariloche | ✅ | ✅ | [PENDIENTE — verificar en Vercel] |
| Parrilla Patagonia Piscis | `san-martin-de-los-andes-2-restaurantes/parrilla-patagonia-piscis` | Restaurante | San Martín de los Andes | ✅ | ✅ | [PENDIENTE — verificar en Vercel] |

---

## Prospectos con detalles.md listos

> Origen: prospección El Chaltén · 2 km · cafe,bar,hostel,restaurant,aventura,hotel · 2026-03-22

| Score | Negocio | Ruta | Rubro | Tel | detalles.md | Sitio |
|-------|---------|------|-------|-----|:-----------:|:-----:|
| 🔥 80 | Lo de Trivi | `el-chalten-2-multi/lo-de-trivi` | Alojamiento | 02966 15-64-6857 | ✅ | ❌ |
| 🔥 80 | Hotel Poincenot | `el-chalten-2-multi/hotel-poincenot` | Hotel | 02962 49-3252 | ✅ | ❌ |
| 🔥 80 | Max | `el-chalten-2-multi/max` | Alojamiento | 0221 318-3455 | ✅ | ❌ |
| 🔥 80 | Posada y Cabañas El Barranco | `el-chalten-2-multi/posada-y-cabanas-el-barranco` | Posada/Cabañas | 02966 76-2332 | ✅ | ❌ |
| 🔥 80 | Posada del Aguila | `el-chalten-2-multi/posada-del-aguila` | Posada | 011 15-3880-3786 | ✅ | ❌ |
| 🔥 80 | Newen | `el-chalten-2-multi/newen` | Alojamiento | 02966 15-44-5587 | ✅ | ❌ |
| 🔥 80 | Lo de Tomy | `el-chalten-2-multi/lo-de-tomy` | Alojamiento | 02966 15-64-6857 | ✅ | ❌ |
| 🔥 80 | Hosteria La Cima | `el-chalten-2-multi/hosteria-la-cima` | Hostería | 02966 52-9067 | ✅ | ❌ |
| 🔥 80 | Hotel Lago del Desierto | `el-chalten-2-multi/hotel-lago-del-desierto` | Hotel | 02966 69-0212 | ✅ | ❌ |
| 🔥 80 | Apart El Caburé | `el-chalten-2-multi/apart-el-cabure` | Apart Hotel | 02962 49-3118 | ✅ | ❌ |
| 🔥 80 | Hospedaje Mi Rincón El Chaltén | `el-chalten-2-multi/hospedaje-mi-rincon-el-chalten` | Hospedaje | 02966 15-65-3075 | ✅ | ❌ |
| 🔥 80 | Hostel Los Viajeros | `el-chalten-2-multi/hostel-los-viajeros` | Hostel | 02966 15-40-3951 | ✅ | ❌ |

> Origen: prospección Potrerillos · 5 km · food · 2026-03-22

| Score | Negocio | Ruta | Rubro | Tel | detalles.md | Sitio |
|-------|---------|------|-------|-----|:-----------:|:-----:|
| 🔥 85 | Farmacia Valles De Potrerillos | `potrerillos-5-food/farmacia-valles-de-potrerillos` | Farmacia | 2612196536 | ✅ | ❌ |
| 🔥 80 | Villa Los Cóndores | `potrerillos-5-food/villa-los-condores` | Alojamiento | 0261 664-5927 | ✅ | ❌ |
| 🔥 80 | CABAÑAS La Guillermina | `potrerillos-5-food/cabanas-la-guillermina` | Cabañas | 0261 460-5683 | ✅ | ❌ |
| ♨️ 75 | Hostel Los Pinos | `potrerillos-5-food/hostel-los-pinos` | Hostel | 0261 206-4444 | ✅ | ❌ |
| ♨️ 75 | Camping El Montañés | `potrerillos-5-food/camping-el-montanes` | Camping | 0261 535-3141 | ✅ | ❌ |
| ♨️ 75 | Cabañas Gran Malvinas | `potrerillos-5-food/cabanas-gran-malvinas` | Cabañas | 0261 612-6336 | ✅ | ❌ |
| ♨️ 75 | Cabañas Benítez | `potrerillos-5-food/cabanas-benitez` | Cabañas | 0261 576-7542 | ✅ | ❌ |
| ♨️ 70 | Casa Potrerillos | `potrerillos-5-food/casa-potrerillos` | Alojamiento | 0261 390-0970 | ✅ | ❌ |

---

## Cómo actualizar este archivo

Cuando se genera y deploya un sitio:
1. Mover la fila a la tabla **"Sitios en producción"**
2. Cambiar el estado de `Sitio` a ✅
3. Agregar la URL de Vercel en la columna URL

Para agregar un nuevo prospecto después de correr `/prospectar`:
1. Agregar una fila en la tabla de prospectos con score y datos del negocio
2. Marcar `detalles.md` como ✅ una vez generado

---

## Archivos de prospección

| Carpeta / Archivo | Descripción |
|-------------------|-------------|
| `potrerillos-5-food/potrerillos-5-food.md` | Búsqueda raw · Potrerillos · 5 km · food · 60 negocios |
| `potrerillos-5-food/potrerillos-5-food-scored.md` | Scoring · 43 evaluados · 8 seleccionados |
| `san-martin-de-los-andes-2-restaurantes/san-martin-de-los-andes-2-restaurantes.md` | Búsqueda raw · San Martín de los Andes |
| `san-martin-de-los-andes-2-restaurantes/san-martin-de-los-andes-2-restaurantes-scored.md` | Scoring · San Martín de los Andes |
| `cerro-otto-bariloche-1-alojamientos/cerro-otto-bariloche-1-alojamientos.md` | Búsqueda raw · Bariloche · alojamientos |
| `el-chalten-2-multi/el-chalten-2-multi.md` | Búsqueda raw · El Chaltén · 2 km · multi-rubro · 131 negocios |
| `el-chalten-2-multi/el-chalten-2-multi-scored.md` | Scoring · 85 evaluados · 12 HOT seleccionados |
