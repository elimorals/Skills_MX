# mp_klap

Klap (BNPL alternativo).

## Estado

- Sin credenciales: datos de ejemplo marcados `simulated: true`
- ⏳ Path real pendiente — requiere implementar HTTP/API

## Credenciales (para path real)

- `KLAP_API_KEY`

## Tools

- `klap_listar_pagos`
- `klap_consultar_pago`

## Setup mock

```bash
.venv/bin/python -m mp_klap.server
```

## Estado real (2026-10-14)

- ❌ **Sin API pública.** No se encontró documentación pública de API de Klap en México.
- Con credenciales configuradas, cada tool devuelve `ConfigError` con `motivo: sin_api_publica` y la alternativa: Exporta los pagos desde el portal de Klap.
- Sin credenciales responde datos simulados marcados `simulated: true` (solo para demos).
