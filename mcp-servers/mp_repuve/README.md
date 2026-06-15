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

## Estado del MCP

| Componente | Estado |
|---|---|
| Estructura (client + server + schemas) | ✅ Listo |
| Mock determinístico | ✅ Funciona |
| Validación NIV (ISO 3779) / placa MX | ✅ Funciona |
| Modo Playwright real | ⚠️ Esqueleto listo, endpoint exacto pendiente captura |
| Tests | ✅ |

**NOTA**: Durante el discovery (2026-06-15) Angular tuvo race conditions
con Playwright que impidieron capturar el endpoint backend en una sola
toma. La infraestructura del MCP (PortalSession + selectores + flow) está
lista; cuando se confirme el endpoint, basta ajustar `API_URL_PATTERN`
en `shared/repuve.py`.

## Tools

### `repuve_consultar_niv(niv)`
Consulta por NIV/VIN (17 caracteres, sin I/O/Q). Devuelve datos del vehículo + estatus.

### `repuve_consultar_placa(placa)`
Consulta por placa mexicana.

### `repuve_verificar_robado(niv=..., placa=...)`
Decisión binaria — devuelve `tiene_reporte_robo: bool` + advertencias.

## Configuración

| Env var | Default | Descripción |
|---|---|---|
| `PLUGINS_MX_MOCK` | `1` | Override mock. |
| `PLUGINS_MX_REPUVE_LIVE` | unset | `1` activa Playwright real. |
| `PLUGINS_MX_CACHE_DIR` | `~/.cache/plugins-mx` | Cache local (7 días). |

## Tests

```bash
PYTHONPATH=mcp-servers pytest mcp-servers/mp_repuve/tests -v
```
