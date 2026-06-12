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
