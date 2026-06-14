# Website comercial — Plugins MX

Landing comercial estática para los 3 productos vendibles del monorepo `plugins-mx`:

- **Cartera Predial** multi-municipio (243 municipios, 163 consultables)
- **Compliance REPSE** Art. 15 LFT (sin captcha, 4M empresas afectadas)
- **ISN-as-a-Service** 32 estados con tasas 1.8% — 3.0%

Pensado para mandar por WhatsApp / LinkedIn a despachos contables, inmobiliarias y áreas fiscales corporativas en lugar de un repo de GitHub.

## Stack

- HTML estático, CSS puro, JS vanilla — sin build step
- **Fraunces** (display serif), **Geist** (body sans), **JetBrains Mono** (datos) — Google Fonts
- IntersectionObserver para scroll reveals y count-up animations
- Magnetic buttons + tilt 3D en cards
- Sin dependencias, sin tracking, ~70 KB total

## Estética

Editorial fiscal mexicano. Cream + tinta + acentos terracotta / maíz / nopal. Sin purple-gradient AI slop. Tipografía gigante con cursivas variables (Fraunces SOFT + WONK axes).

## Deploy

### Opción 1: GitHub Pages (gratis, instant)
```bash
# Desde el repo raíz
git subtree push --prefix website origin gh-pages
# O configurar Pages → /website folder
```
URL final: `https://<usuario>.github.io/Skills_MX/`

### Opción 2: Vercel / Netlify (free tier, dominio custom)
```bash
cd website
vercel deploy --prod
# o
netlify deploy --prod --dir=.
```
Conecta dominio: `plugins-mx.com` o `compliance.cipreholding.com`.

### Opción 3: Cloudflare Pages
Importa el repo, root: `website/`, build command vacío, output: `.`

### Local
```bash
cd website
python3 -m http.server 8080
# o
npx serve
```
Abrir `http://localhost:8080`.

## Personalización

| Archivo | Para qué |
|---|---|
| `index.html` | Landing principal + 8 secciones |
| `productos/predial.html` | Detalle producto 01 |
| `productos/repse.html` | Detalle producto 02 |
| `productos/isn.html` | Detalle producto 03 |
| `styles.css` | Sistema de diseño completo |
| `productos/producto.css` | Estilos exclusivos de páginas detalle |
| `scripts.js` | Animaciones + form handler |

### Cambiar número de WhatsApp
En `scripts.js`, función `handleDemo`, reemplazar `525500000000` por tu número real (formato internacional sin `+` ni espacios).

### Cambiar email
Buscar y reemplazar `elimoralsmendox@gmail.com` en todos los archivos.

### Actualizar stats
Los counters se generan automáticamente de los atributos `data-target="<n>"` y `data-suffix="<sufijo>"` en `index.html`. Solo cambia el atributo y la animación se ajusta.

## Estructura

```
website/
├── index.html                 # Landing principal
├── styles.css                 # Sistema de diseño
├── scripts.js                 # IntersectionObserver + count-up + tilt + form
├── README.md                  # Este archivo
└── productos/
    ├── predial.html
    ├── repse.html
    ├── isn.html
    └── producto.css           # Estilos específicos de producto
```

## Performance

- 0 frameworks · 0 bundlers · 0 build step
- Fonts vía CDN con `preconnect`
- SVG inline para íconos (sin requests adicionales)
- `prefers-reduced-motion` respetado
- Mobile-first, breakpoints en 600px / 768px / 900px

## Próximos pasos sugeridos

1. **Capturar leads de verdad**: cambiar form `mailto` por integración con Formspree, ConvertKit, o webhook al MCP `mp_mercado_pago` para auto-cobrar el setup.
2. **Embeber demo en vivo**: video screencap de 60s consultando 5 muns de cartera predial.
3. **Página de pricing**: tres tiers — POC ($X), Implementación ($Y), Suscripción mensual ($Z).
4. **Blog técnico**: traducir hallazgos del repo (cobertura nacional, descubrimientos del discovery automatizado) a posts SEO en `plugins-mx.com/blog/`.
5. **OG image**: generar tarjeta social 1200×630 PNG con stats principales para LinkedIn/WhatsApp preview.

— Construido junio 2026, durante FASE 60 del monorepo `plugins-mx`.
