# Changelog — core-mexico

Cambios del plugin base mexicano.

Formato: [Keep a Changelog](https://keepachangelog.com).
Versioning: [Semantic Versioning](https://semver.org).

## [Unreleased]

### Added
- `.mcp.json` con `banxico` MCP propio activo por default (modo mock sin credenciales). Implementación en `mcp-servers/mp_banxico/` con 7 tools (TC DOF, UMA, INPC, TIIE, conversión).
- Subagent `validador-cfdi-batch` para auditar lotes grandes de CFDIs
- References bundleados: regímenes fiscales completo, complementos CFDI, integración SAT, ARCO, Banxico, tono MX

### Changed
- `mxn-formato` actualizado para documentar tools del MCP `banxico` directamente, en lugar de solo mencionar Banxico en abstracto.

### Changed
- `cfdi-emision`: agregada sección de datos a verificar vigentes
- `iva-retenciones-mx`: agregadas alertas de tarifas que pueden estar desactualizadas
- `whatsapp-business-mx`: alertas sobre tarifas Meta y aprobación de templates
- `compliance-lfpdppp`: alertas sobre reformas post-2022

## [0.1.0] — 2026-06-11

### Added
- Plugin manifest con 6 skills compartidos
- Skills: cfdi-emision (calidad de referencia), iva-retenciones-mx, rfc-validacion, whatsapp-business-mx, compliance-lfpdppp, mxn-formato
- Commands: /core:validar-rfc, /core:format-mxn, /core:timbrar-cfdi
- 7 references bundleados iniciales
