# Changelog — talleres-mx

Cambios del plugin para talleres mecánicos en México.

Formato: [Keep a Changelog](https://keepachangelog.com).
Versioning: [Semantic Versioning](https://semver.org).

## [Unreleased]

### Added
- Subagent `defensor-profeco` para construir expediente de defensa ante queja PROFECO

### Changed
- `garantia-servicio`: agregada sección de datos PROFECO/NMX a verificar vigentes

## [0.1.0] — 2026-06-11

### Added
- Plugin manifest con 10 skills (4 propios + 6 sincronizados)
- Skills propios:
  - `diagnostico-cotizacion`: flow estructurado con desglose MO + refacciones
  - `autorizacion-cliente-wa`: orquesta autorización vía WhatsApp con bitácora auditada
  - `garantia-servicio`: 30d MO + 90d refacciones (PROFECO mínimo)
  - `orden-trabajo`: OT inicial/modificación/cierre con firmas
- Commands: /talleres:nuevo-diagnostico, /talleres:autorizacion, /talleres:orden-trabajo, /talleres:garantia
- .mcp.json placeholder con Facturama, Gupshup, Mercado Libre, Stripe (disabled)
