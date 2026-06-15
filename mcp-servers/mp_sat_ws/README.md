# mp_sat_ws

MCP para SAT Web Service de Descarga Masiva CFDI. Top 15 #9.

## Por qué importa

El servicio oficial del SAT que permite descargar **TODOS los CFDIs** emitidos o
recibidos en un rango de fechas (hasta 200,000 por solicitud). Complementa
`mp_facturama_extendido` (que solo timbra los emitidos vía PAC).

## Universo

- **Despacho contable**: cierre mensual de 100-500 clientes
- **ERPs (Aspel, Contpaqi, SAP)**: reconciliación CFDI automática
- **Auditoría fiscal**: due-diligence histórica de proveedores/clientes
- **Cripto/fintech**: comprobación de operaciones para Buzón Tributario

## Endpoints

| Endpoint | URL | Función |
|---|---|---|
| Autenticación | `/Autenticacion/Autenticacion.svc` | Token (5 min vigencia) |
| Solicitar | `/SolicitaDescargaService.svc` | Devuelve idSolicitud |
| Verificar | `/VerificaSolicitudDescargaService.svc` | Polling estado |
| Descargar | `/DescargaMasivaService.svc` | ZIP con XMLs |

Base: `https://cfdidescargamasivasolicitud.clouda.sat.gob.mx`

## Tools

### `sat_ws_solicitar_descarga`
Inicia la solicitud. Devuelve `id_solicitud` (UUID).

### `sat_ws_verificar_solicitud`
Polling. `cod_estatus_solicitud == 3` = TERMINADA, lista para descargar.

### `sat_ws_descargar_paquete`
Descarga un ZIP cuando la solicitud está TERMINADA.

## Estado del MCP

- ✅ Estructura SOAP completa (4 endpoints, schemas, error handling)
- ✅ Mock determinístico para CI/dev
- ✅ Validación de RFC + rangos de fecha ISO
- ✅ Tests unitarios
- ⚠️ **Modo real requiere XMLSignature** con e.firma — placeholder en v1.
  Cuando el usuario provea cert/key/password, implementar `_real_solicitud()`
  con `signxml` o `lxml + cryptography`.

## Auth (modo real)

3 env vars requeridas:
```bash
export SAT_EFIRMA_CERT=/path/to/cert.cer
export SAT_EFIRMA_KEY=/path/to/key.key
export SAT_EFIRMA_PASSWORD="..."
export PLUGINS_MX_SAT_WS_LIVE=1
```

Sin estas vars, el MCP corre 100% en mock.

## Limitaciones del SAT

- Hasta **5 solicitudes simultáneas** por RFC.
- Cada solicitud cubre **máximo 200,000 CFDIs**.
- Las solicitudes **expiran a los 7 días**.
- Polling **mínimo cada 30 segundos** (rate limit).

## Tests

```bash
PYTHONPATH=mcp-servers pytest mcp-servers/mp_sat_ws/tests -v
```
