# mp_mercado_libre — Mercado Libre MCP

MCP server para automatizar la operación de un seller en Mercado Libre (México). Mercado Libre concentra ~50% del e-commerce regional y **no tiene MCP oficial** — éste llena el gap.

## Lo que cubre

- **Listings**: listar, ver detalle, pausar/activar, actualizar precio y stock (sync con otros canales).
- **Órdenes**: listar con filtros (status, rango de fechas), ver detalle con flags derivados (`is_paid`, `is_terminal`).
- **Mensajes post-venta**: leer y enviar mensajes en packs (conversaciones de orden).
- **Preguntas pre-venta**: listar las pendientes (`UNANSWERED` por default) y responderlas.
- **Reputación**: nivel del seller, métricas de claims, demoras y cancelaciones.
- **Catálogos**: enums de status descritos en español para que el agente decida sin red.

## Tools expuestos

| Tool | Tipo | Descripción |
|---|---|---|
| `mercadolibre_get_me` | read | Identifica al seller dueño del refresh_token (cache 24h) |
| `mercadolibre_list_items` | read | Lista items con filtro por status y paginación |
| `mercadolibre_get_item` | read | Detalle de un listing + flags `is_reactivable`/`is_terminal` (cache 5min) |
| `mercadolibre_update_stock` | write | Cambia `available_quantity` |
| `mercadolibre_update_price` | write | Cambia el precio |
| `mercadolibre_pause_item` | write | Pausa un listing (desaparece de búsquedas) |
| `mercadolibre_activate_item` | write | Reactiva un listing pausado |
| `mercadolibre_list_orders` | read | Lista órdenes con filtros (status, fechas) |
| `mercadolibre_get_order` | read | Detalle de orden + `is_paid`/`is_terminal` (cache 2min) |
| `mercadolibre_list_messages` | read | Mensajes en un pack post-venta |
| `mercadolibre_send_message` | write | Envía mensaje al comprador |
| `mercadolibre_list_questions` | read | Preguntas pre-venta (default: UNANSWERED) |
| `mercadolibre_answer_question` | write | Responde una pregunta |
| `mercadolibre_get_seller_reputation` | read | Métricas + nivel del seller (cache 30min) |
| `mercadolibre_listar_catalogos` | read | Discovery offline de enums |

## Configuración

### Credenciales (modo real)

ML usa OAuth 2.0. Necesitas:
1. Registrar una app en https://developers.mercadolibre.com.mx
2. Obtener `client_id` (= `ML_APP_ID`) y `client_secret` (= `ML_SECRET`)
3. Correr el flujo OAuth authorize **una vez** en navegador para obtener el `refresh_token` (válido 6 meses):

```
https://auth.mercadolibre.com.mx/authorization?response_type=code&client_id=APP_ID&redirect_uri=...
```

4. Exportar como env vars:

```bash
export ML_APP_ID="..."
export ML_SECRET="..."
export ML_REFRESH_TOKEN="..."
```

El MCP refresca el `access_token` (TTL 6h) automáticamente y guarda en cache cifrado. Si ML rota el refresh_token, lo persiste en cache también.

### Modo mock (sin credenciales)

Si no hay credenciales o defines `PLUGINS_MX_MOCK=1`, el cliente devuelve datos determinísticos plausibles:

- `get_item("MLM...1")` → status `active` (último dígito impar)
- `get_item("MLM...2")` → status `paused` (último dígito par)
- `get_order("12345")` → `paid` (impar)
- `get_order("12346")` → `payment_required` (par)
- `get_order("cancelled")` → `cancelled`

Útil para desarrollo, demos y tests de plugins sin tocar la cuenta real.

## Seguridad y compliance

- **PII en bitácora**: `pack_id`, `buyer_id`, `question_id` se hashean antes de loggear. El contenido del mensaje solo registra `text_len`.
- **Moderación ML**: el MCP no la implementa — confía en el agente. Pero los docstrings de `send_message` y `answer_question` recuerdan que compartir números, emails o links externos viola los TOS y puede banear la cuenta.
- **Rate limits**: ~5000 req/hora por app. El cache ayuda (especialmente en `get_me`, `get_item`, `get_seller_reputation`).

## Integración con plugins

Copia `example.mcp.json` al `.mcp.json` del plugin que lo necesite. Hoy lo usa:
- `core-mexico` (universal)
- `talleres-mx` (gestión de inventario + post-venta)

## Tests

```bash
.venv/bin/pytest mp_mercado_libre/tests -v
```

63 tests cubren: catálogos (helpers), OAuth (rotation, cache, errores 400/401), client (mock determinístico, cache, bitácora), tools FastMCP (validación pydantic + comportamiento end-to-end).
