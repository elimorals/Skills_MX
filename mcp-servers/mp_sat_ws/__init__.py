"""mp_sat_ws — MCP para SAT Web Service de Descarga Masiva CFDI.

Servicio SOAP oficial del SAT que permite descargar TODOS los CFDIs emitidos
o recibidos en un rango de fechas (hasta 200,000 por solicitud).

Requiere e.firma vigente del contribuyente (certificado .cer + llave .key
+ contraseña). NO usa CIEC ni RFC+password.

Universo:
  - Despacho contable: cierre mensual de 100-500 clientes
  - ERPs (Aspel, Contpaqi, SAP): reconciliación CFDI automática
  - Auditoría fiscal: due-diligence histórica
  - Cripto/fintech: comprobación de operaciones para Buzón Tributario

4 endpoints SOAP:
  1. /Autenticacion → token (5 min vigencia)
  2. /SolicitaDescargaService → idSolicitud (queue del SAT)
  3. /VerificaSolicitudDescargaService → polling hasta status=3 (TERMINADA)
  4. /DescargaMasivaService → ZIP con XMLs
"""
__all__: list[str] = []
