# mp_edomex_municipal — Portales Estado de México

## Tools (4)

| Tool | Qué devuelve |
|---|---|
| `edomex_consultar_predial` | Toluca: consulta real por httpx. Otros municipios: Playwright genérico del catálogo central |
| `edomex_consultar_tenencia` | Handoff humano al portal de recaudación + reglas de subsidio 2026 |
| `edomex_consultar_multas` | Handoff humano a infracciones.ssedomex.gob.mx (Cloudflare Turnstile) |
| `edomex_listar_catalogos` | Municipios, portales, Hoy No Circula |

Datos simulados solo con `PLUGINS_MX_MOCK=1`. Sin fallback silencioso a mock.

## Estado real (2026-10-14)

| Consulta | URL | Status | Resultado |
|---|---|---|---|
| Predial Toluca | http://predial.toluca.gob.mx/Formas/ImpuestoPredial.aspx | 200 (GET+POST) | Real. Clave ficticia `0000000000000000` → "La Clave Catastral no está registrada" (`not_found`) |
| Tenencia | https://pagosytramites.edomex.gob.mx/recaudacion/ | 200 | Flujo por placa no verificado → handoff humano |
| Multas | https://infracciones.ssedomex.gob.mx/Search | 200 | Turnstile → handoff humano |
| Predial Ecatepec | http://www.tesoreriaecatepec.gob.mx/IngresosTesoreria/ | 404 | Falla con `upstream_error` |
| Predial Naucalpan | https://naucalpan.gob.mx/predial/ | — | Certificado TLS vencido → `upstream_error` |
| Predial Cuautitlán Izcalli | http://201.122.109.4:96/EstadoCuentaOnline/ | — | Timeout → `upstream_error` |

La respuesta exitosa de Toluca trae el nombre del propietario: no se devuelve.
El parser de la tabla de liquidación no se ha visto con una clave real (requiere
la de un particular). Test live parametrizado:
`TOLUCA_CLAVE_CATASTRAL=<16 dígitos> PLUGINS_MX_LIVE=1 pytest -m live mp_edomex_municipal`.

Subsidio tenencia 2026 (confianza media, notas de prensa N+/UnoTV): 100% si la
factura es ≤ $638,000 con IVA y placas 2021+ (50% placas 2020). Refrendo $990.

## Tests

```bash
cd mcp-servers && .venv/bin/pytest -q mp_edomex_municipal
```
