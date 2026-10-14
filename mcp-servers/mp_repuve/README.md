# mp_repuve

MCP para REPUVE (Registro Público Vehicular). Top 15 #5.

## Por qué importa

- **Universo**: aseguradoras, movilidad (Uber/DiDi/Cabify), marketplaces de usados
  (Kavak, Clutch), despachos de leasing, RRHH con flotilla.
- **Caso de uso típico**: rechazar póliza/contratar/listar si tiene_reporte_robo.

## Portal

- **URL**: https://www2.repuve.gob.mx:8443/ciudadania/
- **Stack**: Angular SPA + reCAPTCHA v3 invisible
- **Site key reCAPTCHA**: `6Lfy8AEoAAAAANclz0Doczn6y826fM0BjOPXEn9B`
- 4 modos de búsqueda: placa, número de serie (NIV), folio, número de constancia

## Estado real

| Fecha | URL | Resultado |
|---|---|---|
| 2026-10-14 | `GET https://www2.repuve.gob.mx:8443/ciudadania/` | 200, Angular + reCAPTCHA v3 invisible |
| 2026-10-14 | `POST https://www2.repuve.gob.mx:8443/consulta/consulta/repuve` desde Chromium headless | 401 "El reCaptcha no fue superado correctamente" |
| 2026-10-14 | mismo endpoint sin token (test live) | 401 reCaptcha |
| 2026-10-14 | `GET /ciudadania/main.b6696a0b2d85ae16.js` (bundle público) | sitekey `6Lfy8AEoAAAAANclz0Doczn6y826fM0BjOPXEn9B`, acción `login`; `criterio`/`llave` cifrados RSA-1024 PKCS#1 v1.5 (node-forge) + base64 con llaves públicas fijas `publicKeyRep` (/repuve) y `publicKeyPgj` (/pgj, estatus de robo) |

- Estado: **con solver opt-in: real sin validar en vivo (falta llave)**.
  Con `PLUGINS_MX_CAPTCHA_SOLVER=2captcha` + `TWOCAPTCHA_API_KEY`: lee sitekey y
  llaves RSA del bundle en vivo (respaldo: constantes en `shared/repuve.py`),
  pide token reCAPTCHA v3 (acción `login`), cifra `criterio` ("1" placa, "2" NIV)
  y `llave`, y consulta `/repuve` (vehículo) y `/pgj` (estatus de robo). Si REPUVE
  responde 401 reCaptcha se reintenta 2 veces y luego `UpstreamError`.
  El cifrado es reproducible porque las llaves son públicas y fijas en el JS; no
  hay llave por sesión ni otro anti-bot (el `rpv.min.js` externo llega vacío).
- Pendiente de validar en vivo: forma exacta de la respuesta (dict de listas,
  como la recorre el portal) y valores de `ESTATUS_VHI_ROBO`. Si `/pgj` falla,
  `tiene_reporte_robo: null` con advertencia (no se cachea).
- Sin solver: **handoff humano** (`requiere_humano: true`, URL, pasos, NIV/placa
  prellenado) y `repuve_verificar_robado` devuelve `tiene_reporte_robo: null`
  (desconocido), nunca `false`.
- Live: `PLUGINS_MX_LIVE=1 TWOCAPTCHA_API_KEY=… REPUVE_LIVE_PLACA=<placa propia>`.
- El servidor solo negocia cifrados TLS legacy (`@SECLEVEL=1`).
- Mock solo con `PLUGINS_MX_MOCK=1` (`simulated: true`).

## Tools

### `repuve_consultar_niv(niv)`
Consulta por NIV/VIN (17 caracteres, sin I/O/Q). Devuelve datos del vehículo + estatus.

### `repuve_consultar_placa(placa)`
Consulta por placa mexicana.

### `repuve_verificar_robado(niv=..., placa=...)`
Devuelve `tiene_reporte_robo` (bool en mock; `null` + handoff en real) + advertencias.

## Configuración

| Env var | Default | Descripción |
|---|---|---|
| `PLUGINS_MX_MOCK` | unset | `1` = datos simulados (`simulated: true`). |
| `PLUGINS_MX_CACHE_DIR` | `~/.cache/plugins-mx` | Cache local (7 días). |

## Tests

```bash
PYTHONPATH=mcp-servers pytest mcp-servers/mp_repuve/tests -v
```
