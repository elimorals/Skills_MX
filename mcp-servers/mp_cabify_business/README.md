# mp_cabify_business

Movilidad corporativa con la [Ride-Hailing API v4 de Cabify](https://developers.cabify.com/docs/ride-hailing).

## Estado real (2026-10-14)

- ✅ Reescrito contra la referencia oficial (OpenAPI de cabify-api.readme.io): OAuth2
  `client_credentials` en `/auth/api/authorization` y endpoints `/api/v4/estimates`,
  `/api/v4/journey`, `/journey/{id}`, `/journey/{id}/state` (GET estado, POST cancelar) y `/journey/{id}/sales`.
- ❌ Eliminados `cabify_list_rides` y `cabify_generate_invoice`: apuntaban a endpoints
  inventados (`api.cabify.com/v1/rides`, `/v1/invoices`). La API no tiene listado de viajes
  ni genera CFDI; los recibos por viaje salen de `cabify_ventas_viaje`.
- ⚠️ **Sin validar en vivo**: falta una integración de sandbox.
- Sin credenciales responde datos simulados `simulated: true`; con credenciales, los errores se propagan.

## Credenciales

- `CABIFY_CLIENT_ID` (OAuth UUID) y `CABIFY_CLIENT_SECRET` — panel Cabify Business → Integración.
- `CABIFY_ENV` — `production` (default) o `sandbox` (credenciales distintas).

## Tools

| Tool | Endpoint |
|---|---|
| `cabify_estimar` | `POST /api/v4/estimates` — obligatorio antes de pedir viaje |
| `cabify_pedir_viaje` | `POST /api/v4/journey` — **genera cargo** |
| `cabify_consultar_viaje` | `GET /api/v4/journey/{id}` |
| `cabify_estado_viaje` | `GET /api/v4/journey/{id}/state` |
| `cabify_cancelar_viaje` | `POST /api/v4/journey/{id}/state` (409 si ya no se puede) |
| `cabify_ventas_viaje` | `GET /api/v4/journey/{id}/sales` |
| `cabify_listar_catalogos` | estados de viaje (local) |

## Prueba en vivo (sandbox)

```bash
PLUGINS_MX_LIVE=1 CABIFY_ENV=sandbox CABIFY_CLIENT_ID=... CABIFY_CLIENT_SECRET=... \
  .venv/bin/pytest -q mp_cabify_business/tests/test_all.py::test_live_token_sandbox
```
