# Changelog — freelancers-mx

Cambios del plugin para freelancers, consultores y agencias unipersonales en México.

Formato: [Keep a Changelog](https://keepachangelog.com).
Versioning: [Semantic Versioning](https://semver.org).

## [Unreleased]

### Added
- Subagent `auditor-fiscal-mensual` para auditoría completa mes antes de declarar
- Subagent `revisor-cobranza-cartera` para visión panorámica de cartera

### Changed
- `freelance-tax-mx`: agregada sección de riesgo regulatorio CRÍTICO con datos a verificar
- `cobranza-seguimiento`: agregada sección de datos legales a verificar

## [0.1.0] — 2026-06-11

### Added
- Plugin manifest con 11 skills (5 propios + 6 sincronizados)
- Skills propios:
  - `cotizacion-mxn`: cotización formato MX con IVA y retenciones
  - `propuesta-comercial`: propuestas 3-15 páginas con SOW, T&Cs, PI, NDA
  - `cobranza-seguimiento`: 5 etapas escaladas con templates MX
  - `cliente-onboarding`: captura fiscal completa + contrato marco
  - `freelance-tax-mx`: pago provisional ISR (RESICO/PFAE)
- Commands: /freelancers:cotizar, /freelancers:propuesta, /freelancers:cobranza, /freelancers:onboarding, /freelancers:pago-provisional
- .mcp.json placeholder con Facturama, Notion, Stripe (disabled)
