---
name: generar-sitio
description: Toma el slug de un negocio, crea el repo en GitHub, genera el sitio Next.js basado en detalles.md, hace commit/push y deploya en Vercel con auto-deploy configurado.
argument-hint: "[nombre-negocio]"
---

# Skill: Generar Sitio Web y Deployar en Vercel

## Input

Extraé del argumento:
- **nombre-negocio** — slug del negocio (ej: `los-ciervos`). Debe coincidir con una carpeta existente en `negocios/[nombre-negocio]/`.

---

## Paso 0 — Verificar prerequisitos

1. Verificá que existe `negocios/[nombre-negocio]/detalles.md`. Si no existe, reportá el error y detené.
2. Verificá que `gh` está autenticado: `gh auth status`. Si falla, pedile al usuario que corra `gh auth login`.
3. Verificá que `vercel` está instalado: `vercel --version`. Si no está, pedile que corra `npm i -g vercel`.

---

## Paso 1 — Crear repositorio en GitHub

Creá el repositorio público en GitHub:

```bash
gh repo create [nombre-negocio]-web --public --description "Sitio web de [nombre-negocio]" --confirm
```

Si el repo ya existe, continuá con el siguiente paso sin error.

Guardá la URL del repo: `https://github.com/[usuario]/[nombre-negocio]-web`

Para obtener el usuario actual: `gh api user --jq .login`

---

## Paso 2 — Clonar en la carpeta del negocio

```bash
mkdir -p negocios/[nombre-negocio]/web
git clone git@github.com:[usuario]/[nombre-negocio]-web negocios/[nombre-negocio]/web
```

Si el directorio ya tiene contenido (clone previo), hacé `git pull` en lugar de clonar.

---

## Paso 3 — Preparar el contexto para generación

Copiá el `detalles.md` del negocio a la raíz de la carpeta web (el prompt lo espera ahí):

```bash
cp negocios/[nombre-negocio]/detalles.md negocios/[nombre-negocio]/web/detalles.md
```

---

## Paso 4 — Generar el sitio

Leé el archivo `prompts/prompt.md` — ese es el prompt maestro de generación.

Luego leé `negocios/[nombre-negocio]/web/detalles.md` como fuente de verdad del contenido.

Ejecutá el prompt completo: generá toda la estructura del proyecto Next.js dentro de `negocios/[nombre-negocio]/web/`. Esto incluye crear todos los archivos del sitio (package.json, tsconfig, app/, components/, etc.) tal como indica `prompts/prompt.md`.

**Reglas:**
- Todo el contenido viene de `detalles.md`. Nunca inventar datos ni usar lorem ipsum.
- Si un campo está marcado `[PENDIENTE]`, dejá un comentario `// TODO:` en el código.
- El estilo visual a usar es el que indique el usuario en los argumentos. Si no lo indicó, **preguntarle antes de generar** (opciones 1 al 5 según `prompts/prompt.md`).

---

## Paso 5 — Commit y push

Desde `negocios/[nombre-negocio]/web/`:

```bash
cd negocios/[nombre-negocio]/web
git add .
git commit -m "feat: initial site generation for [nombre-negocio]"
git push origin main
```

Si el branch por defecto es `master`, usá `master`.

---

## Paso 6 — Deploy en Vercel

Desde `negocios/[nombre-negocio]/web/`, linkeá el proyecto con Vercel y deployá a producción:

```bash
cd negocios/[nombre-negocio]/web
vercel link --yes
vercel --prod --yes
```

`vercel link` crea el proyecto en Vercel y lo conecta al directorio. Si ya existe un proyecto con ese nombre, lo linkea automáticamente.

Guardá la URL de producción que devuelve Vercel (formato: `https://[nombre-negocio]-web.vercel.app` o similar).

---

## Paso 7 — Conectar GitHub para auto-deploy

Para que cada `git push` deploye automáticamente en producción, conectá el repo de GitHub al proyecto de Vercel:

```bash
cd negocios/[nombre-negocio]/web
vercel git connect --yes
```

Si `vercel git connect` no está disponible en la versión instalada, informale al usuario que puede conectarlo manualmente desde el dashboard de Vercel:
1. Ir a `vercel.com/dashboard`
2. Abrir el proyecto `[nombre-negocio]-web`
3. Settings → Git → Connect Git Repository → seleccionar `[nombre-negocio]-web`

Una vez conectado, **cada push a `main` deploya automáticamente en producción**.

---

## Paso 8 — Resumen final

```
✅ Sitio generado y deployado

🏗️  Negocio:     [nombre-negocio]
📦 Repo GitHub: https://github.com/[usuario]/[nombre-negocio]-web
🌐 URL Vercel:  [url-produccion]
📁 Local:       negocios/[nombre-negocio]/web/

🔄 Auto-deploy: cada push a main → producción automática

👉 Para iterar:
   cd negocios/[nombre-negocio]/web
   # editá lo que necesites
   git add . && git commit -m "..." && git push
```

---

## Manejo de errores

| Situación | Acción |
|-----------|--------|
| `detalles.md` no existe | Reportar y sugerir correr `/prospectar` primero |
| Repo GitHub ya existe | Continuar, no es error |
| Clone falla (SSH key) | Sugerir `gh ssh-key add` o cambiar a HTTPS |
| `vercel link` pide login | Sugerir `vercel login` antes de continuar |
| `vercel git connect` falla | Dar instrucciones para conectar manualmente desde el dashboard |
| Campo `[PENDIENTE]` en detalles.md | Generar con `// TODO:` en el código, no bloquear |
