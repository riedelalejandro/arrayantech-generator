---
name: analizar-prospectos
description: Recibe los datos de un negocio y devuelve su score de probabilidad de compra de un sitio web (0-100), tier, breakdown de puntos y ángulo de venta. Diseñado para ser llamado por un agente que le pasa la info y usa el output.
argument-hint: "nombre=[...] dirección=[...] teléfono=[...] sitio_web=[...] rating=[...] cantidad_reseñas=[...] categorías=[...]"
---

# Skill: Scoring de Prospecto

## Input

Recibís los siguientes datos de un negocio (pueden venir como JSON, como texto o como argumentos):

```
nombre          string
dirección       string | null
teléfono        string | null
sitio_web       string | null
rating          number (0 si no tiene)
cantidad_reseñas number (0 si no tiene)
estado          string (ej: "OPERATIONAL")
categorías      string[] (ej: ["lodging", "establishment"])
```

---

## Sistema de Scoring (0–100 pts)

### Criterio 1 — Presencia digital ausente (35 pts máx)

| Condición | Puntos |
|-----------|--------|
| Sin sitio web (`sitio_web` es null) | +20 |
| Sin teléfono (`teléfono` es null) | +10 |
| 0 reseñas (`cantidad_reseñas` == 0) | +5 |

### Criterio 2 — Atractivo del rubro (30 pts máx)

Usá la categoría con mayor puntaje si hay múltiples.

| Categorías | Puntos |
|------------|--------|
| `dentist`, `doctor`, `health`, `physiotherapist`, `beauty_salon`, `spa` | 30 |
| `lawyer`, `accounting`, `real_estate_agency`, `insurance_agency` | 28 |
| `hotel`, `lodging` | 25 |
| `gym`, `fitness_center` | 25 |
| `restaurant`, `cafe`, `bar`, `bakery` | 22 |
| `car_repair`, `car_dealer` | 22 |
| `electrician`, `plumber`, `painter`, `contractor` | 20 |
| `school`, `tutoring` | 20 |
| `florist`, `jewelry_store`, `clothing_store` | 18 |
| `pet_store`, `veterinary_care` | 18 |
| `hardware_store`, `furniture_store` | 15 |
| Otros | 10 |

### Criterio 3 — Validación del negocio (20 pts máx)

| Condición | Puntos |
|-----------|--------|
| Rating ≥ 4.0 | +10 |
| Rating entre 3.0 y 3.9 | +5 |
| Más de 20 reseñas | +10 |
| Entre 5 y 19 reseñas | +5 |

### Criterio 4 — Facilidad de contacto (15 pts máx)

| Condición | Puntos |
|-----------|--------|
| Tiene teléfono | +10 |
| Dirección completa (tiene número de calle) | +5 |

---

## Clasificación por tier

| Score | Tier |
|-------|------|
| 80–100 | 🔥 HOT |
| 60–79 | ♨️ WARM |
| 40–59 | 🌡️ TEPID |
| 0–39 | ❄️ COLD |

---

## Output

Devolvé **únicamente** un JSON con esta estructura, sin texto adicional:

```json
{
  "nombre": "...",
  "score": 75,
  "tier": "WARM",
  "breakdown": {
    "sin_web": 20,
    "sin_telefono": 10,
    "sin_reseñas": 0,
    "rubro": 25,
    "rating": 10,
    "reseñas": 10,
    "telefono": 0,
    "direccion": 5
  },
  "por_que": "Tiene 99 reseñas y 4 estrellas pero ninguna presencia web propia.",
  "angulo_venta": "Tus 99 clientes que te dejan 4 estrellas no pueden reservar online — un sitio con formulario de reservas captura directamente a los turistas que te buscan en Google."
}
```

`por_que` y `angulo_venta` solo para tier HOT y WARM. Para TEPID y COLD dejá ambos como `null`.
