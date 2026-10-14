# mp_paypal_mx

PayPal MX para comerciantes: transacciones y saldos vía
[Transaction Search API v1](https://developer.paypal.com/api/transaction-search/v1/). Solo lectura.

## Estado real (2026-10-14)

- ✅ Cliente real contra el schema OpenAPI oficial: OAuth2 `client_credentials`,
  `GET /v1/reporting/transactions` y `GET /v1/reporting/balances`.
- ⚠️ **Sin validar en vivo**: falta una app REST (sandbox o live) con credenciales.
- Sin credenciales responde datos simulados marcados `simulated: true`.
  Con credenciales, cualquier error de PayPal se propaga (`AuthError`, `NotFoundError`, `UpstreamError`).

## Credenciales

- `PAYPAL_CLIENT_ID`, `PAYPAL_CLIENT_SECRET` — app REST del Dashboard de PayPal
  con la opción **Transaction Search** activada.
- `PAYPAL_ENV` — `live` (default) o `sandbox`.

## Límites de PayPal

- Máximo 31 días por consulta; `page_size` hasta 500.
- Las transacciones tardan hasta 3 h en aparecer.

## Tools

- `paypal_mx_listar_transacciones(fecha_inicio?, fecha_fin?, pagina?, tamano_pagina?)`
- `paypal_mx_consultar_transaccion(transaction_id, fecha_inicio?, fecha_fin?)`
- `paypal_mx_balance(moneda?, al_momento?)`

## Prueba en vivo (sandbox)

```bash
PLUGINS_MX_LIVE=1 PAYPAL_ENV=sandbox PAYPAL_CLIENT_ID=... PAYPAL_CLIENT_SECRET=... \
  .venv/bin/pytest -q mp_paypal_mx/tests/test_all.py::test_live_balance_sandbox
```
