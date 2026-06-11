# Changelog — colegios-mx

Cambios del plugin para colegios privados K-12 en México.

Formato: [Keep a Changelog](https://keepachangelog.com).
Versioning: [Semantic Versioning](https://semver.org).

## [Unreleased]

### Changed
- `cfdi-colegiaturas-deducibles`: agregada sección de alto riesgo regulatorio con datos a verificar (topes Art. 151, versión complemento InsEduc)

## [0.1.0] — 2026-06-11

### Added
- Plugin manifest con 10 skills (4 propios + 6 sincronizados)
- Skills propios:
  - `cobranza-colegiaturas`: 5 etapas con tono empático para padres
  - `comunicacion-padres-wa`: catálogo templates UTILITY por categoría
  - `constancias-academicas`: inscripción, estudios, boleta, parcial
  - `cfdi-colegiaturas-deducibles`: UsoCFDI D10 + complemento InsEduc
- Commands: /colegios:cobranza, /colegios:aviso-padres, /colegios:constancia, /colegios:facturar-colegiatura
- .mcp.json placeholder con Facturama, Gupshup (WA), Stripe (disabled)
