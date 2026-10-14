# mp_rappi_partners

Restaurantes en Rappi México vía la [API de integración de Rappi](https://dev-portal.rappi.com/en/api-reference/content/).

## Estado real (2026-10-14)

- ✅ Cliente real contra el dev-portal: login `POST /restaurants/auth/v1/token/login/integrations`
  (token 24 h, header `x-authorization: Bearer`), órdenes `GET /orders` y `/orders/status/sent`,
  menú `GET /menu/rappi/{storeId}`, disponibilidad `PATCH /restaurants/menu/v1/stores/{storeId}/products/SKU/stock`.
- ⚠️ **Sin validar en vivo**: Rappi entrega credenciales solo a aliados aprobados (contacto comercial).
- ❌ `rappi_consultar_ranking_zona` y `rappi_estimar_comisiones_mes`: la API no tiene esos datos
  (solo órdenes nuevas, sin histórico). Con credenciales devuelven `ConfigError` `motivo: sin_endpoint`.
- `rappi_consultar_orden` busca entre las órdenes nuevas: la API no tiene GET por ID.
- Sin credenciales responde datos simulados `simulated: true`.

## Credenciales

- `RAPPI_CLIENT_ID`, `RAPPI_CLIENT_SECRET` — entregadas por Rappi al aprobar la integración.
- `RAPPI_STORE_ID` — ID de la tienda.
- `RAPPI_ENV` — `mx` (default: `api.rappi.com.mx` + `services.mxgrability.rappi.com`) o `dev`.

## Prueba en vivo (entorno dev de Rappi)

```bash
PLUGINS_MX_LIVE=1 RAPPI_ENV=dev RAPPI_CLIENT_ID=... RAPPI_CLIENT_SECRET=... RAPPI_STORE_ID=... \
  .venv/bin/pytest -q mp_rappi_partners/tests/test_all.py::test_live_listar_ordenes
```
