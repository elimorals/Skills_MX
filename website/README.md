# website/ — sitio público de Plugins MX

Sitio estático en Vercel (https://skills-mexico.vercel.app). Resume el [README raíz](../README.md), que es la fuente de verdad: 40 plugins de Claude Code, 342 skills, 83 MCPs / 417 tools, 26 workflows, 17 scripts de hooks (12 registrados), 12 handlers de webhook y 1,900 tests. Licencia Apache-2.0.

Destaca tres casos de uso con su estado real al 2026-10-14:

- **Cartera Predial**: catálogo de 243 municipios; Toluca, Querétaro y Monterrey consultan en vivo, CDMX entrega a humano (ALTCHA), el resto sin revalidar.
- **Compliance REPSE** (Art. 15 LFT): validado en vivo, sin CAPTCHA.
- **ISN**: cálculo local con tasas 2026 de 2.5% a 4.25% (fuente secundaria).

## Stack

HTML estático, CSS y JS sin build. Fuentes de Google Fonts. `api/lead-demo.js` es la única función de Vercel (reenvía el formulario de demo por correo con Resend; requiere `RESEND_API_KEY`).

## Qué se genera y qué se edita a mano

`scripts/generar-estado-mcps.py` genera, desde la sección "Estado real" de cada `mcp-servers/mp_*/README.md` y los catálogos de `mcp-servers/shared/`:

- `data/*.json` y sus copias en `api/` (`mcp-estado`, `skills-catalog`, `portales-coverage`, `municipios`, `isn-tasas`)
- `mcp-manifest.json` (`description`, `servers`, `stats`)
- los bloques entre `<!-- …:inicio -->` / `<!-- …:fin -->` de `index.html`, `llms.txt`, `llms-full.txt`, `productos/isn.html` y `glosario/isn/index.html`

No edites eso a mano: cambia el script o el README del MCP y corre `python3 scripts/generar-estado-mcps.py`; `--check` falla si algo quedó desactualizado. Lo demás (páginas, `data/repse-stats.json`, `openapi.json`, `.well-known/`) se edita a mano.

## Local

```bash
cd website && python3 -m http.server 8080
```

## Deploy

Vercel con raíz `website/`, sin build command. `vercel.json` define `cleanUrls`, las reescrituras de `/api/*.json` a `/data/` y los headers.

## Estructura

```
website/
├── index.html            Landing: estado de MCPs, 40 plugins por sector, workflows, instalación, límites
├── marketplace/          Explorador de los 83 MCPs (lee /api/skills-catalog.json)
├── portales/             Portales por estado y dependencia (lee /api/portales-coverage.json)
├── guias/                Guía de CFDI 4.0 y recetas que enlazan al MCP o workflow en el repo
├── productos/            Predial, REPSE, ISN
├── glosario/             REPSE, ISN, predial
├── sobre/                Autor
├── llms.txt, llms-full.txt, openapi.json, mcp-manifest.json, .well-known/
└── data/, api/           JSON estáticos (no hay API REST de consulta)
```
