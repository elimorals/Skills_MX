"""mp_isn_mx — MCP multi-estado para Impuesto sobre Nómina (ISN) MX.

Universo: TODA empresa formal con al menos 1 trabajador (~4M empresas).
Mayor universo de cualquier MCP del monorepo.

Patrón: catálogo central de 32 estados (8 validados) + auto-routing por estado.

Cada estado tiene su portal propio (CDMX SAC, JAL gobiernoenlinea1, NL egobierno,
EdoMex sfpya, etc.) pero la API conceptual es la misma:
- calcular_isn(nomina, estado)
- listar_estados()
- generar_linea_captura(estado, periodo, rfc) — path real, mock por default
- descargar_declaracion(estado, periodo, rfc) — path real, mock por default
"""
