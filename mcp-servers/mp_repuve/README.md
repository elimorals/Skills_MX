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

- Estado: **handoff humano**. El body se cifra en el navegador (`criterio`,
  `llave`) y lleva token reCAPTCHA v3; un navegador automatizado es rechazado.
  No se evade: las tools devuelven `requiere_humano: true`, URL, pasos y el
  NIV/placa prellenado.
- `repuve_verificar_robado` en modo real devuelve `tiene_reporte_robo: null`
  (desconocido), nunca `false`.
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
