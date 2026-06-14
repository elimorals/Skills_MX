"""mp_dof_api — MCP para consulta del Diario Oficial de la Federación.

DOF = publicación oficial del gobierno MX. Toda ley, decreto, NOM, sanción,
autorización ITF, modificación regulatoria publicada AQUÍ tiene efectos legales.

Universo afectado:
- Despachos legales (monitoreo de leyes/sentencias)
- Despachos contables (cambios fiscales — RMF, anexos)
- Compliance horizontal (sanciones, NOMs aplicables al negocio)
- Áreas de regulación corporativa
- Periodistas / investigadores

Fuente oficial: https://www.dof.gob.mx/
- 100% público, sin captcha, sin login
- HTML simple, fechas DD/MM/YYYY, códigos numéricos por nota
- Búsqueda full-text gratis

Endpoints reales (validados Playwright MCP 2026-06-14):
- Sumario diario:  index_111.php?year=YYYY&month=MM&day=DD
- Detalle nota:    nota_detalle.php?codigo=NNNNNNN&fecha=DD/MM/YYYY
- Búsqueda texto:  busqueda_detalle.php?textobusqueda=TEXTO&choosePath=textoCompleto
"""
