# mp_kueski

Kueski Pay (BNPL Buy Now Pay Later).

## Estado

- ✅ Mock-first
- ⏳ Path real pendiente — requiere implementar HTTP/API

## Credenciales (para path real)

- `KUESKI_API_KEY`

## Tools

- `kueski_listar_pagos` — mock-first
- `kueski_consultar_pago` — mock-first
- `kueski_cancelar_pago` — mock-first

## Setup mock

```bash
.venv/bin/python -m mp_kueski.server
```

## Estado real (2026-10-14)

- ❌ **Sin API pública.** La API de comercio de Kueski Pay solo se entrega a comercios afiliados; no hay referencia pública verificable.
- Con credenciales configuradas, cada tool devuelve `ConfigError` con `motivo: sin_api_publica` y la alternativa: Pide a Kueski acceso a su API de comercio o usa su plugin de e-commerce.
- Sin credenciales responde datos simulados marcados `simulated: true` (solo para demos).
