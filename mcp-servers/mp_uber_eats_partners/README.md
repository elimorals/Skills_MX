# mp_uber_eats_partners

MCP para restaurantes en Uber Eats MX. Mock-first.

## Setup real (humano)

1. Solicitar Marketplace API access en https://developer.uber.com/docs/eats
2. Obtener `client_id` + `client_secret` + `store_id`
3. Setear env vars correspondientes
4. Implementar OAuth + HTTP en `client.py` (reemplazar `raise McpError`)

## Tools

6 tools idénticos en estructura a `mp_rappi_partners` y `mp_didi_food_partners`.

## Notas

- Uber Eats usa estados en MAYÚSCULAS (`DELIVERED`, `IN_PROGRESS`) — distinto a Rappi (español lowercase)
- Comisión típica: 30% (varía por contrato)

## Estado real (2026-10-14)

- ❌ **Sin API pública verificable.** La doc de la Marketplace API devuelve 404 sin sesión de socio,
  así que no se implementan endpoints sin poder verificarlos.
- Con credenciales, cada tool devuelve `ConfigError` `motivo: sin_api_publica` con la alternativa.
- Sin credenciales responde datos simulados `simulated: true` (solo demos).
