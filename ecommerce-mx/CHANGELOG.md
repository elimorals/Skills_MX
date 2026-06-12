# CHANGELOG — ecommerce-mx

Sigue [Keep a Changelog](https://keepachangelog.com/) y [Semver](https://semver.org/).

## [0.1.0] — 2026-06-11

### Added
- Scaffolding inicial del plugin con 5 skills propios:
  - `mercado-libre-listings`
  - `mercado-libre-pricing`
  - `shopify-mx`
  - `inventario-multicanal`
  - `paqueteria-mx`
- 5 comandos slash:
  - `/ecommerce:sync-inventario`
  - `/ecommerce:optimizar-pricing`
  - `/ecommerce:publicar-listing`
  - `/ecommerce:cotizar-envio`
  - `/ecommerce:cierre-ventas`
- 1 agent: `workflow-sync-multicanal`
- Herencia de 6 skills `_shared/` vía core-mexico
- `.mcp.json` con `mp_mercado_libre` activo y placeholders para `mp_shopify_mx`, `mp_amazon_mx_seller`
- README + CHANGELOG + plugin.json

### Estado
- Lint-passing en todos los skills
- Score honesto estimado: 4.5/9 (scaffolding denso)
- **No usar en producción** hasta validar con seller MX real
