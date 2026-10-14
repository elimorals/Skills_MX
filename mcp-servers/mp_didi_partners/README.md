# mp_didi_partners

DiDi (movilidad pasajeros) para conductores.

## Estado

- ✅ Mock-first
- ⏳ Path real pendiente — requiere implementar HTTP/API

## Credenciales (para path real)

- `DIDI_DRIVER_TOKEN`

## Tools

- `didi_partners_listar_viajes` — mock-first
- `didi_partners_consultar_viaje` — mock-first
- `didi_partners_comisiones_mes` — mock-first

## Setup mock

```bash
.venv/bin/python -m mp_didi_partners.server
```

## Estado real (2026-10-14)

- ❌ **Sin API pública.** DiDi no publica API para conductores.
- Con credenciales configuradas, cada tool devuelve `ConfigError` con `motivo: sin_api_publica` y la alternativa: Descarga el resumen de ganancias desde la app DiDi Conductor o tus CFDI de retenciones en el SAT.
- Sin credenciales responde datos simulados marcados `simulated: true` (solo para demos).
