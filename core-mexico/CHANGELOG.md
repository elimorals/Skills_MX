# Changelog — core-mexico

Cambios del plugin base mexicano.

Formato: [Keep a Changelog](https://keepachangelog.com).
Versioning: [Semantic Versioning](https://semver.org).

## [Unreleased]

### Added
- `.mcp.json` con `banxico` MCP propio activo por default (modo mock sin credenciales). Implementación en `mcp-servers/mp_banxico/` con 7 tools (TC DOF, UMA, INPC, TIIE, conversión).
- `.mcp.json` con `facturama` MCP propio activo por default. Implementación en `mcp-servers/mp_facturama_extendido/` con 8 tools (validación local pre-timbrado, timbrar, cancelar, consultar estatus, descargar XML/PDF, buscar, catálogos).
- `.mcp.json` con `mercadopago` MCP propio activo por default. Implementación en `mcp-servers/mp_mercado_pago/` con 9 tools (create_preference, get_payment, list_payments, refund, cancel, validate_webhook_signature HMAC-SHA256, listar_catalogos).
- `.mcp.json` con `mercadolibre` MCP propio activo por default (no hay MCP oficial). Implementación en `mcp-servers/mp_mercado_libre/` con 15 tools (get_me, list_items, get_item con flags derivados, update_price, update_stock, pause/activate, list_orders, get_order, list/send messages, list/answer questions, get_seller_reputation, listar_catalogos). OAuth 2.0 con refresh automático y rotation handling.
- `.mcp.json` con `curp_renapo` MCP propio activo por default. Implementación en `mcp-servers/mp_curp_renapo/` con 9 tools (validar_estructura, derivar_fecha/sexo/estado, validar_lote, generar_desde_datos, consultar_renapo, descargar_constancia_renapo, listar_catalogos). 8 de 9 tools son 100% locales (regex + dígito verificador SAT, sin red). RENAPO en modo mock — Playwright + CAPTCHA pendientes.
- `.mcp.json` con `banxico_cep` MCP propio activo por default. Implementación en `mcp-servers/mp_banxico_cep/` con 10 tools (validar_clabe, decodificar_clabe, parsear_clave_rastreo, lookup_banco, generar_cep, validar_cep, descargar_pdf, consultar_pago_por_clave, listar_bancos, listar_catalogos). 4 tools locales (CLABE 18-dígitos con pesos cíclicos 3,7,1, parseo heurístico de claves SPEI por prefijo) son 100% reales. Las 4 que tocan Banxico arrancan en mock determinístico — Banxico no tiene API REST oficial, Playwright pendiente. Catálogo de ~80 bancos + casas de bolsa + fintechs (BBVA, Banamex, Mercado Pago, STP, NU, Stori, etc.). Cierra el ciclo de conciliación bancaria SPEI ↔ CFDI.
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
