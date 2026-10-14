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

- Firma XMLDSig (RSA-SHA1, exc-c14n) implementada en `SatWsClient._firmar_soap_request`,
  portada de [phpcfdi/sat-ws-descarga-masiva](https://github.com/phpcfdi/sat-ws-descarga-masiva) (MIT).
  Solo depende de `cryptography` (extra `[sat-ws]`).
- Flujo real completo: Autenticación (token WRAP, se reutiliza 4 min) →
  SolicitaDescargaEmitidos/Recibidos → VerificaSolicitudDescarga → Descargar.
- Sin fallback a mock con credenciales: un `CodEstatus` distinto de 5000 levanta
  `UpstreamError` con `details.cod_estatus_sat` (300-305, 404, 5002, 5005…); un
  SOAP Fault de seguridad levanta `AuthError`.
- Mock solo con `PLUGINS_MX_MOCK=1` o sin `SAT_EFIRMA_*` (respuestas `simulated: true`).
- `sat_descargar_cfdi_masivo` de `mp_sat_portal` usa este cliente para la solicitud del mes.

## Estado real (validación en vivo)

| Qué | Cómo se validó | Resultado |
|---|---|---|
| Firma byte a byte | `tests/test_firma.py`: DigestValue y SignatureValue idénticos a los requests de phpcfdi con la e.firma de prueba EKU9003173C9; firma verificada con la llave pública; digest re-verificado una vez con exc-c14n de `lxml` | OK |
| Autenticación | 2026-10-14, `POST .../Autenticacion/Autenticacion.svc` con la e.firma **de prueba** EKU9003173C9 | HTTP 200, token devuelto |
| Verifica / Descargar | 2026-10-14, mismas credenciales de prueba, id ficticio | `CodEstatus 305 Certificado Inválido` (el SAT parsea el sobre y la firma; rechaza el certificado de prueba, esperado) |
| Solicitud / Verifica / Descarga con e.firma real | **No validado.** Pendiente de correr `test_live.py` con la e.firma del usuario | — |

No se probó `SolicitaDescarga` en vivo: crea una solicitud real (consume cupo del SAT).

## Auth (modo real)

```bash
pip install -e '.[sat-ws]'
export SAT_EFIRMA_CERT=/path/to/cert.cer      # DER
export SAT_EFIRMA_KEY=/path/to/key.key        # PKCS#8 DER cifrado
export SAT_EFIRMA_PASSWORD="..."
```

Sin estas vars (o con `PLUGINS_MX_MOCK=1`) el MCP corre en mock.

## Limitaciones del SAT

- Hasta **5 solicitudes simultáneas** por RFC.
- Cada solicitud cubre **máximo 200,000 CFDIs**.
- Las solicitudes **expiran a los 7 días**.
- Polling **mínimo cada 30 segundos** (rate limit).
- Recibidos en XML: el SAT solo acepta `EstadoComprobante=Vigente` (el cliente lo fija).
- `rfc_emisor` debe ser el RFC de la e.firma cargada (si no, `ValidationError`).

## Tests

```bash
cd mcp-servers && .venv/bin/pytest -q mp_sat_ws
# en vivo (solo Autenticación, no crea solicitudes):
PLUGINS_MX_LIVE=1 SAT_EFIRMA_CERT=... SAT_EFIRMA_KEY=... SAT_EFIRMA_PASSWORD=... \
  .venv/bin/pytest -q mp_sat_ws/tests/test_live.py
```

Fixtures: respuestas XML del SAT tomadas de phpcfdi/sat-ws-descarga-masiva (MIT). El repo no
incluye ninguna e.firma: los tests generan una autofirmada al vuelo (`tests/efirma_prueba.py`).
Las comparaciones byte a byte contra phpcfdi necesitan la e.firma de prueba del SAT
(EKU9003173C9, RFC-PAC-SC.zip) en una carpeta fuera del repo:
`SAT_EFIRMA_PRUEBA_DIR=/ruta/con/EKU9003173C9.{cer,key} y EKU9003173C9-password.txt`; sin ella se saltan.
