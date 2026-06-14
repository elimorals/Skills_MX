"""mp_donatarias_sat — MCP para padrón de donatarias autorizadas SAT.

Las donatarias autorizadas son las únicas OSC/ONG facultadas por SAT para emitir
recibos deducibles de ISR (Art. 79 Fracc. VI LISR + Art. 27 Fracc. I-V).

Universo afectado:
- ~10,000 donatarias autorizadas activas en MX
- Toda persona física/moral que dona y quiere deducir
- Despachos contables que asesoran ONG
- Empresas con CSR/responsabilidad social

Fuente oficial:
- Portal: https://www.sat.gob.mx/consultas/27717/conoce-el-directorio-de-donatarias-autorizadas
- Anexo 14 RMF anual + actualizaciones DOF
- Excel descargable: omawww.sat.gob.mx/cifras_sat/Documents/Padron[Año].xlsx

Crítico para verticales:
- donatarias-ongs-mx (validar status propio)
- despacho-contable-mx (validar status de cliente al cierre fiscal)
- core-mexico (validar receptor antes de emitir CFDI con uso D04 = Donativos)
"""
