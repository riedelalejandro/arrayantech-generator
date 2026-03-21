# Prompt: Sitio Web de Negocio con Next.js + Turbopack → Vercel

## Rol

Sos un desarrollador frontend senior especializado en Next.js, diseño de conversión y performance web. Tu tarea es construir un sitio web completo, production-ready, para deployar en Vercel.

---

## Paso 0 — Leer el archivo de negocio

**Antes de escribir una sola línea de código**, leé el archivo `detalles.md` que está en la raíz del proyecto. Ese archivo contiene toda la información del negocio:

- Nombre, rubro e industria
- Propuesta de valor
- Público objetivo y sus dolores
- Producto o servicio y sus features
- Prueba social (testimonios, métricas, logos)
- Planes y precios
- Preguntas frecuentes
- Paleta de colores, tipografía y tono de voz
- Links y datos de contacto

**Todo el contenido del sitio debe venir de `detalles.md`**. No inventes datos, no uses lorem ipsum. Si un campo está vacío o marcado como `[PENDIENTE]`, dejá un comentario `// TODO:` en el código indicando qué falta.

---

## Stack Técnico

```
Framework:     Next.js 15 (App Router)
Bundler:       Turbopack (next dev --turbo)
Estilos:       Tailwind CSS v4
Animaciones:   Framer Motion
Iconos:        Lucide React
Deploy:        Vercel
Lenguaje:      TypeScript estricto
```

---

## Estructura del Proyecto

```
/
├── app/
│   ├── layout.tsx          # Metadata global, fuentes, Analytics
│   ├── page.tsx            # Página principal (ensambla todas las secciones)
│   └── globals.css         # Variables CSS y estilos base
├── components/
│   ├── sections/
│   │   ├── Hero.tsx
│   │   ├── Problem.tsx
│   │   ├── Solution.tsx
│   │   ├── SocialProof.tsx
│   │   ├── Pricing.tsx
│   │   ├── Faq.tsx
│   │   └── Footer.tsx
│   └── ui/
│       ├── Button.tsx
│       ├── Badge.tsx
│       └── SectionWrapper.tsx
├── lib/
│   └── content.ts          # Exporta los datos de detalles.md como objetos TS
├── public/
│   └── images/
├── detalles.md             # ← Fuente de verdad del negocio
├── next.config.ts
├── tailwind.config.ts
└── package.json
```

---

## Configuración Inicial

### `package.json`
```json
{
  "scripts": {
    "dev": "next dev --turbo",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  }
}
```

### `next.config.ts`
```ts
import type { NextConfig } from 'next'

const config: NextConfig = {
  experimental: {
    turbo: {},
  },
  images: {
    formats: ['image/avif', 'image/webp'],
  },
}

export default config
```

### `vercel.json` (opcional, para headers de performance)
```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "X-Frame-Options", "value": "DENY" }
      ]
    }
  ]
}
```

---

## `lib/content.ts` — Puente entre `detalles.md` y los componentes

Creá este archivo como la única fuente de datos para todos los componentes. Los valores deben reflejar exactamente lo que está en `detalles.md`:

```ts
export const siteConfig = {
  business: { /* nombre, tagline, descripción corta */ },
  hero: { /* headline, subheadline, CTA principal, CTA secundario, imagen o video */ },
  problem: { /* título, lista de dolores del usuario */ },
  solution: { /* título, features con ícono, descripción y beneficio */ },
  socialProof: { /* testimonios[], logos[], métricas[] */ },
  pricing: { /* planes[], CTA de cada plan, nota de garantía */ },
  faq: { /* preguntas[], respuestas[] */ },
  footer: { /* links, redes sociales, legal, contacto */ },
  theme: { /* colores primarios, fuente, tono */ },
}
```

---

## Estructura de Secciones — Especificación Detallada

### 1. Hero
**Objetivo:** Comunicar qué es el producto y para quién en menos de 3 segundos.

**Debe incluir:**
- Headline principal (H1): la propuesta de valor en una línea. Máximo 10 palabras. Sin jerga.
- Subheadline: expande el H1 con contexto. 1-2 oraciones.
- CTA primario: botón con acción clara ("Empezar gratis", "Ver demo", "Contratar ahora")
- CTA secundario: enlace menos prominente ("Ver cómo funciona ↓")
- Elemento visual: imagen del producto, mockup, video corto o ilustración. No stock photos genéricas.
- Social proof mínima: "Usado por +500 empresas" o similar, debajo del CTA

**Técnico:**
- Animación de entrada con Framer Motion (`fadeInUp` staggered para headline → subheadline → CTAs)
- LCP optimizado: imagen con `priority` en `next/image`
- Responsive: en mobile el visual va debajo del texto

---

### 2. Problem
**Objetivo:** Hacer que el visitante piense "esto es exactamente lo que me pasa".

**Debe incluir:**
- Título que nombra el dolor (no la solución)
- 3 a 5 puntos de dolor específicos del público objetivo, extraídos de `detalles.md`
- Cada punto: ícono + texto corto. Sin bullets genéricos.
- Tono: empático, no alarmista

**Técnico:**
- Grid de cards animadas con `whileInView` de Framer Motion
- Fondo diferenciado del Hero (gris claro o color de acento suave)

---

### 3. Solution
**Objetivo:** Mostrar cómo el producto resuelve cada dolor mencionado en la sección anterior.

**Debe incluir:**
- Título que introduce la solución
- Features: mínimo 3, máximo 6. Cada feature tiene:
  - Ícono (Lucide React)
  - Nombre del feature
  - Beneficio concreto (qué logra el usuario, no qué hace la feature)
- Screenshot, demo o ilustración del producto en uso
- Si hay video: autoplay muted loop, sin controles visibles

**Técnico:**
- Layout alternado en desktop: texto izquierda / imagen derecha, luego imagen izquierda / texto derecha
- Lazy loading en imágenes secundarias

---

### 4. Social Proof
**Objetivo:** Eliminar el escepticismo con evidencia real.

**Puede incluir (según lo que haya en `detalles.md`):**
- Testimonios: foto, nombre, cargo, empresa, cita. Mínimo 3.
- Logos de clientes o marcas conocidas
- Métricas: "98% de satisfacción", "+10.000 usuarios", "$2M ahorrados"
- Casos de éxito resumidos (antes/después)

**Técnico:**
- Testimonios en carousel en mobile, grid en desktop
- Logos en marquee animado si hay más de 6
- Las métricas deben animarse con contador al entrar en viewport

---

### 5. Pricing
**Objetivo:** Que el visitante no tenga excusa para no elegir un plan.

**Debe incluir:**
- 2 o 3 planes máximo (más confunde)
- Plan destacado (el más elegido) con borde o badge visual
- Lista de qué incluye cada plan
- CTA individual por plan
- Nota de garantía o política de cancelación ("Sin contrato", "14 días gratis", etc.)
- Toggle mensual/anual si aplica (con descuento visible en anual)

**Técnico:**
- El plan recomendado se anima con un `scale(1.04)` sutil
- Accesible: estructura de tabla semántica bajo el hood

---

### 6. FAQ
**Objetivo:** Resolver las objeciones que no se respondieron antes y dar el último empujón.

**Debe incluir:**
- Mínimo 5 preguntas, máximo 8
- Preguntas reales que haría alguien escéptico (precio, seguridad, soporte, cancelación)
- Accordion accesible (aria-expanded, aria-controls)
- Debajo del accordion: CTA final con mensaje de urgencia o garantía

**Técnico:**
- Accordion nativo con animación de altura en Framer Motion (`AnimatePresence`)
- No usar librerías externas para esto

---

### 7. Footer
**Objetivo:** Credibilidad, navegación secundaria y datos legales.

**Debe incluir:**
- Logo + tagline corto
- Links de navegación agrupados por categoría
- Redes sociales
- Email de contacto
- Copyright y links legales (Términos, Privacidad)

---

## Componentes UI Reutilizables

### `Button.tsx`
```tsx
// Variantes: primary | secondary | ghost
// Tamaños: sm | md | lg
// Props: href (para Link), onClick, loading, disabled
```

### `SectionWrapper.tsx`
```tsx
// Aplica padding vertical consistente
// Acepta: id (para scroll), className, children
// Anima entrada con Framer Motion whileInView
```

---

## Diseño y Estilo

Leé la sección `## Diseño` de `detalles.md` para:
- Color primario y secundario → definir en `globals.css` como variables CSS
- Tipografía → cargar desde `next/font/google` en `layout.tsx`
- Tono de voz → aplicar en todos los copies

**Reglas generales:**
- Mobile-first: diseñar para 375px, luego escalar
- Espaciado consistente: usar escala de 4px (4, 8, 12, 16, 24, 32, 48, 64, 96)
- Contraste mínimo WCAG AA en todo el texto
- No usar más de 2 familias tipográficas
- No usar imágenes de stock genéricas

---

## Estilos Visuales — Elegí uno antes de ejecutar

Antes de generar el código, el usuario debe indicar **qué estilo visual aplicar**.
La instrucción es: **"Usá el Estilo [NÚMERO/NOMBRE]"**.

Cada estilo define: paleta, tipografía, layout, animaciones y personalidad.
Los colores del negocio en `detalles.md` se integran dentro del sistema del estilo elegido
(como color de acento o color primario), pero la estructura visual y el carácter del estilo
prevalecen sobre las preferencias genéricas del archivo.

---

### Estilo 1 — CLEAN SAAS
**Personalidad:** Confianza, claridad, velocidad. El estilo de los productos B2B que respetan el tiempo del usuario.
**Referentes:** Linear, Vercel, Raycast, Resend

#### Paleta
```css
--background: #FFFFFF;
--surface:    #F7F7F5;      /* cards, secciones alternas */
--border:     #E5E5E3;
--text-primary:   #0A0A0A;
--text-secondary: #6B6B6B;
--accent:     [color primario de detalles.md];
--accent-fg:  #FFFFFF;
```

#### Tipografía
```
Display:  Geist (next/font/local, ya incluida en Next.js 15)
Body:     Geist (misma familia, pesos 400/500)
Mono:     Geist Mono (para badges de código o features técnicas)
Escala:   Hero H1 → 56px/600, H2 → 36px/500, body → 16px/400
```

#### Layout y componentes
- Fondo blanco puro. Cards con borde `1px solid var(--border)`, sin sombra.
- Sections alternas: blanco → `--surface` → blanco.
- Grid de 12 columnas. Hero centrado con max-width 680px para el texto.
- Botones: border-radius 6px. Primary sólido, Secondary outline fino.
- Separadores: líneas `1px` muy suaves, nunca decorativos.
- Íconos: Lucide, tamaño 16px, stroke 1.5px, alineados con el texto.

#### Animaciones
- Entrada de secciones: `fadeInUp` 0.4s ease-out, stagger 80ms entre elementos.
- Hover en cards: `translateY(-2px)` + ligero cambio de border-color.
- Sin animaciones llamativas. Todo debe sentirse rápido y quirúrgico.
- Métricas: contador numérico simple al entrar en viewport.

#### Navbar
- Sticky, blanco con blur `backdrop-filter: blur(12px)` al hacer scroll.
- Logo a la izquierda, links centrados, CTA a la derecha.
- Border-bottom `1px` que aparece al scrollear.

#### Hero específico
- Texto centrado. Headline con un `<mark>` o span de acento en la palabra clave.
- Badge pequeño arriba del headline: "Nuevo ✦ Feature X" o social proof número.
- CTA primario + CTA ghost. Sin imagen héroe — el producto habla por sí solo o mockup mínimo.

---

### Estilo 2 — DARK PREMIUM
**Personalidad:** Exclusividad, sofisticación, alto valor percibido. Para productos que no compiten en precio.
**Referentes:** Stripe, Anthropic, Vercel (dark), Perplexity

#### Paleta
```css
--background: #0A0A0A;
--surface:    #111111;
--surface-2:  #1A1A1A;
--border:     rgba(255,255,255,0.08);
--border-hover: rgba(255,255,255,0.16);
--text-primary:   #F5F5F3;
--text-secondary: #888884;
--accent:     [color primario de detalles.md, versión brillante];
--accent-glow: [accent con 30% opacity para glows sutiles];
```

#### Tipografía
```
Display:  Cal Sans o Instrument Serif (para headlines con carácter)
          Alternativa: Playfair Display si el negocio es más artesanal/premium
Body:     Inter (400/450)
Escala:   Hero H1 → 64px/600 con letter-spacing -0.02em
          H2 → 40px/500, body → 16px/400, line-height 1.7
```

#### Layout y componentes
- Fondo `#0A0A0A`. Cards con `border: 1px solid var(--border)` + `background: var(--surface)`.
- Efecto "spotlight": radial gradient muy sutil de acento detrás del hero.
- Separadores: líneas con gradiente de transparente → border → transparente.
- Botones: Primary con `background: var(--accent)` y glow box-shadow sutil. Ghost con border semitransparente.
- Pricing: card destacada con border de acento + glow exterior.

#### Animaciones
- Hero: palabras del headline con `staggerChildren` 0.05s, cada palabra aparece con `opacity 0→1` + `y: 20→0`.
- Cards: `whileInView` con `opacity` + escala `0.97→1`.
- Gradient animado muy lento en el fondo del hero (15s loop, casi imperceptible).
- Efecto parallax sutil en el visual del hero al hacer scroll.

#### Navbar
- Fondo negro con blur. Sin border en estado normal, border sutil al scrollear.
- Logo puede ser blanco o en color acento.

#### Hero específico
- Headline en 2 líneas con una palabra o frase en color acento o gradient de texto.
- Subheadline en `--text-secondary`.
- Pill/badge con animación de borde brillante (border-gradient animado).
- Elemento visual: mockup con glow de fondo o gradiente radial de acento.

---

### Estilo 3 — BOLD EDITORIAL
**Personalidad:** Arriesgado, memorable, opinionado. Para marcas que quieren diferenciarse con actitud.
**Referentes:** Linear (landing vieja), Lemon.fm, Basement Studio, algunas páginas de Figma

#### Paleta
```css
--background: #F2EFE8;      /* crema/papel */
--surface:    #E8E4DC;
--ink:        #0D0D0D;       /* casi negro para texto display */
--text-primary:   #1A1A1A;
--text-secondary: #5A5A5A;
--accent:     [color primario de detalles.md — debe ser vibrante];
--accent-dark: [versión oscura del acento para hover];
--rule:       #0D0D0D;       /* líneas negras de regla editorial */
```

#### Tipografía
```
Display:  Syne (800/900) — geométrico y con personalidad fuerte
          Alternativa: Space Grotesk 700 si Syne es demasiado agresivo
Body:     DM Sans (400/500)
Regla:    Tamaños extremos — Hero H1 hasta 80px en desktop, reducir a 44px mobile
          Números grandes en métricas: 96px/900
Letter-spacing: display → -0.03em, body → normal
```

#### Layout y componentes
- Fondo crema. Uso intensivo de líneas negras como separadores de secciones (`border-top: 2px solid var(--rule)`).
- Cards: sin border-radius o radius mínimo (4px). Flat y rectangular.
- Grid asimétrico en algunas secciones: 7/5 columns en lugar de 6/6.
- Elementos tipográficos decorativos: número de sección en display enorme y transparente como fondo ("01", "02"...).
- Botones: rectangulares, sin border-radius. Primary con fondo negro o acento. Hover invierte colores.
- Íconos: mínimos, preferir arrows y elementos tipográficos (→, ↗) sobre íconos ilustrativos.

#### Animaciones
- Entrada: `clipPath` de `inset(100% 0 0 0)` a `inset(0% 0 0 0)` — texto que "emerge" de abajo.
- Stagger por línea de texto en el headline del hero.
- Hover en cards: borde negro que aparece, leve desplazamiento del texto.
- Sin parallax. Las animaciones son de reveal, no de movimiento continuo.

#### Navbar
- Sin fondo fijo. Logo + menú en texto plano. CTA con borde negro.
- Al scrollear: aparece con fondo crema y `border-bottom: 2px solid var(--rule)`.

#### Hero específico
- Headline en múltiples líneas con texto enorme que ocupa el ancho.
- Una palabra o línea en color acento o con subrayado grueso.
- Layout split: texto izquierda (60%), elemento visual derecha en recuadro con borde.
- Número grande semitransparente como elemento decorativo de fondo.

---

### Estilo 4 — SOFT MODERN
**Personalidad:** Accesible, cálido, humano. Para productos de consumo, salud, educación o cualquier rubro donde la confianza emocional importa más que la frialdad técnica.
**Referentes:** Notion, Loom, Superhuman onboarding, productos de wellness

#### Paleta
```css
--background: #FAFAF8;
--surface:    #F0EEE8;
--surface-2:  #FFFFFF;
--border:     #E2DFD8;
--text-primary:   #1C1C1A;
--text-secondary: #706E68;
--accent:     [color primario de detalles.md — preferir tonos cálidos];
--accent-light: [acento al 12% opacity para fondos de badges];
--success:    #2D9A67;
--warning:    #E07B2A;
```

#### Tipografía
```
Display:  Plus Jakarta Sans (700/800) — moderno sin ser frío
          Alternativa: Nunito (800) para rubros más amigables (salud, kids, educación)
Body:     Plus Jakarta Sans (400/500)
Escala:   Hero H1 → 52px/700, H2 → 36px/600
          Interlineado generoso: body line-height 1.75
          Letter-spacing: display → -0.01em
```

#### Layout y componentes
- Fondo off-white suave. Sections con fondo `--surface` para crear separación sin líneas.
- Cards: border-radius grande (16px). Sombra muy suave `box-shadow: 0 2px 12px rgba(0,0,0,0.06)`.
- Avatares y fotos con border-radius completo (testimonios).
- Botones: border-radius 10px. Primary con background acento. Hover: `brightness(0.92)`.
- Íconos en "pill" de fondo: `background: var(--accent-light)`, ícono en color acento.
- Pricing: cards con bordes suaves, el plan destacado con fondo acento oscuro y texto blanco.

#### Animaciones
- Entrada suave: `opacity 0→1` + `y: 16→0`, duration 0.5s ease-out.
- Stagger generoso: 120ms entre elementos del mismo grupo.
- Hover en cards: `scale(1.02)` + sombra más pronunciada.
- Métricas: contador animado con easing out.
- Sin movimientos abruptos. Todo debe sentirse como respirar.

#### Navbar
- Blanco con sombra sutil desde el inicio.
- Links con hover underline de color acento.
- CTA con fondo acento y border-radius 8px.

#### Hero específico
- Layout centrado. Headline con una palabra en color acento.
- Avatar stack (3-4 fotos de usuarios) + "Usado por X personas" justo debajo del CTA.
- Elemento visual: mockup con sombra suave o ilustración plana con colores cálidos.
- Fondo del hero: radial gradient muy sutil de acento-light en el centro.

---

### Estilo 5 — BRUTALIST MODERN
**Personalidad:** Directo, honesto, sin filtros. Para marcas que tienen algo concreto que decir y lo dicen sin rodeos. Genera recordación inmediata.
**Referentes:** Figma (algunas landings), Gumroad, Arc Browser (parcialmente), mmm.page

#### Paleta
```css
--background: #FFFFFF;
--ink:        #000000;
--surface:    #F0F0F0;
--border:     #000000;     /* bordes siempre negros y visibles */
--text-primary:   #000000;
--text-secondary: #555555;
--accent:     [color primario de detalles.md — usar sin mezclar, puro];
--accent-fg:  #000000;     /* texto NEGRO sobre el acento, no blanco */
```

#### Tipografía
```
Display:  Archivo Black (900) o ABC Whyte (si está disponible)
          Alternativa accesible: Barlow Condensed (800) o Anton
Body:     IBM Plex Sans (400/500) — ligeramente técnico, combina bien
Escala:   Hero H1 → 72px/900 en desktop, line-height 1.0 (comprimido)
          H2 → 48px/900, body → 15px/400
          Uppercase en subtítulos de sección (tracking: 0.08em)
```

#### Layout y componentes
- Bordes negros `2px solid #000` en todos los cards y contenedores importantes.
- Box-shadow como offset: `4px 4px 0px #000` en lugar de sombras difusas.
- Sin border-radius o radius 0px. Todo rectangular.
- Sections separadas con `border-top: 3px solid #000`.
- Botones: rectangular, border `2px solid #000`, hover → background negro, texto blanco (o inverso).
- Color acento se usa como fondo de una sección completa o como highlight de palabras.
- Íconos: reemplazar por flechas tipográficas (→, ↗, ↓) y símbolos (+, ×).
- Pricing: tablas con borders visibles en todas las celdas.

#### Animaciones
- Mínimas y funcionales. Sin easing suave — usar `ease-in` más marcado.
- Hover: desplazamiento del box-shadow (`4px 4px` → `6px 6px`), efecto de "presión".
- Entrada: `opacity` simple. Sin movimiento vertical.
- Una animación de marquee horizontal con el nombre del negocio o un claim repetido.

#### Navbar
- Border-bottom `2px solid #000` fijo. Fondo blanco siempre.
- Logo en tipografía de display (no imagen). CTA con fondo acento.
- Sin efecto de blur ni transparencias.

#### Hero específico
- Headline que ocupa todo el ancho disponible (`font-size: clamp(40px, 8vw, 96px)`).
- Una línea o palabra con fondo de color acento (highlight directo en el texto).
- Layout asimétrico: texto 65% / elemento visual 35%, con borde entre ellos.
- Elemento visual: screenshot con borde negro grueso y box-shadow offset.
- Badge de social proof con borde negro y fondo acento.

---

### Cómo indicar el estilo al ejecutar el prompt

Al inicio de tu mensaje, escribí:

```
Usá el Estilo 1 — CLEAN SAAS
```
o simplemente:
```
Estilo 3
```

Si no indicás ningún estilo, el modelo debe preguntar antes de escribir código.

---

## Performance y SEO

En `app/layout.tsx` configurar:

```tsx
export const metadata: Metadata = {
  title: '...', // Desde detalles.md
  description: '...', // Desde detalles.md
  openGraph: {
    title: '...',
    description: '...',
    images: ['/og-image.png'],
  },
  twitter: { card: 'summary_large_image' },
}
```

**Checklist antes de deployar:**
- [ ] `next build` sin errores ni warnings de TypeScript
- [ ] Lighthouse Performance > 90 en mobile
- [ ] Todas las imágenes con `alt` descriptivo
- [ ] Sin `console.log` en producción
- [ ] Variables de entorno sensibles en `.env.local` (nunca hardcodeadas)
- [ ] `robots.txt` y `sitemap.xml` generados (usar `next-sitemap` o App Router metadata)

---

## Deploy en Vercel

1. Hacer push a GitHub/GitLab
2. Importar el repo en [vercel.com](https://vercel.com)
3. Vercel detecta Next.js automáticamente — no cambiar nada en Build Settings
4. Agregar variables de entorno en el dashboard de Vercel si las hay
5. Deploy automático en cada push a `main`

**Dominio:** configurar en Vercel → Settings → Domains

---

## Resultado Esperado

Un sitio web de una sola página (`/`) con las 7 secciones en orden:

```
Hero → Problem → Solution → Social Proof → Pricing → FAQ → Footer
```

Que sea:
- Rápido (Turbopack en dev, optimizado en build)
- Hermoso y con identidad visual propia (no genérico)
- Orientado a conversión (cada sección tiene un objetivo claro)
- Fácil de actualizar (todo el contenido en `detalles.md` → `lib/content.ts`)
- Listo para producción en Vercel con un solo `git push`
