# mp_tijuana_municipal

## Tools

| Tool | Estado |
|---|---|
| `tijuana_mun_consultar_vivienda_asegurada(clave_catastral)` | Real: Programa de Protección Ciudadana (consulta pública). |
| `tijuana_mun_consultar_predial(clave_catastral)` | Handoff humano (`motivo: login`): el adeudo solo se ve con cuenta del contribuyente o Llave BC. |

## Estado real

| Fecha | URL | Resultado |
|---|---|---|
| 2026-10-14 | `GET https://pagos.tijuana.gob.mx/pagosEnLinea/index.aspx` | 200, formulario de login (usuario/contraseña, Llave BC) |
| 2026-10-14 | `POST https://pagos.tijuana.gob.mx/PagosEnLinea/seguro/index.aspx` (postback `tbPredialSeguro=AA000001`) | 200, `lbMsjSeguro`: "Clave catastral no asegurada" |

Sin CAPTCHA en la consulta de vivienda asegurada. Mock solo con `PLUGINS_MX_MOCK=1`.
Test live: `PLUGINS_MX_LIVE=1 pytest mp_tijuana_municipal -m live` (opcional `TIJ_CLAVE_CATASTRAL`).
