# mp_mercado_pago

Cliente MCP para Mercado Pago — pasarela dominante en LATAM (especialmente B2C y ecommerce).

## Por qué este MCP

- **Sin MCP oficial** — Mercado Pago no publica uno
- **Flujo crítico**: cobrar vía payment link → recibir webhook → emitir CFDI automático
- **Validación HMAC de webhooks incluida** (sin esto, cualquiera puede mandar POSTs falsos al endpoint y disparar emisión de CFDIs por pagos que nunca ocurrieron)
- **Modo mock** con preference_ids determinísticos (sha256 del payload) para tests reproducibles

## Setup

### 1. Obtener access token

1. Registra cuenta en https://www.mercadopago.com.mx/developers
2. Crea una aplicación
3. Copia el access token (sandbox empieza con `TEST-`, producción con `APP_USR-`)

### 2. Configurar

```bash
export MERCADOPAGO_ACCESS_TOKEN="TEST-xxx-xxx-xxx"
```

El environment (sandbox vs production) se detecta automáticamente por el prefijo del token. No hay variable separada para configurarlo.

### 3. (Opcional) Probar sin token

Sin `MERCADOPAGO_ACCESS_TOKEN` corre en **modo mock**:
- `preference_id` determinístico (sha256 del payload — mismo input siempre regresa mismo id)
- Pagos simulados con status según el id (impar → approved, par → pending, "reject" → rejected)
- Webhooks se validan localmente con cualquier secret (no hace red)

```bash
# Forzar mock incluso con token configurado (testing)
export PLUGINS_MX_MOCK=1
```

## Correr el servidor

```bash
cd mcp-servers
.venv/bin/python -m mp_mercado_pago.server
```

## Configurar en Claude Code

```json
{
  "mcpServers": {
    "mercadopago": {
      "command": ".venv/bin/python",
      "args": ["-m", "mp_mercado_pago.server"],
      "cwd": "/Users/elias/Documents/Trabajo/skills/mcp-servers",
      "env": {
        "MERCADOPAGO_ACCESS_TOKEN": "${MERCADOPAGO_ACCESS_TOKEN:-}",
        "PLUGINS_MX_MOCK": "${PLUGINS_MX_MOCK:-}"
      },
      "disabled": false
    }
  }
}
```

## Tools disponibles

### `mercadopago_create_preference`
Genera URL pública (`init_point`) para enviar al cliente.

```python
{
  "items": [{"title": "Consultoría", "quantity": 1, "unit_price": 1500, "currency_id": "MXN"}],
  "payer_email": "cliente@ejemplo.com",
  "external_reference": "cot-123",
  "notification_url": "https://tu-webhook.com/mp",
  "back_url_success": "https://tu-app/gracias",
  "back_url_failure": "https://tu-app/error",
  "back_url_pending": "https://tu-app/pendiente",
  "expires": true,
  "expiration_date_to": "2026-04-15T23:59:59.000-06:00"
}
# →
{
  "preference_id": "...",
  "init_point": "https://www.mercadopago.com.mx/checkout/...",
  "sandbox_init_point": "https://sandbox.mercadopago.com.mx/...",
  "external_reference": "cot-123",
  "simulated": true | false
}
```

### `mercadopago_validate_webhook_signature` ⚠ CRÍTICO PARA SEGURIDAD

Valida HMAC-SHA256 de webhooks entrantes. **SIN esta validación, cualquiera puede mandar POSTs falsos.**

```python
{
  "x_signature": "ts=1742068800,v1=abc123...",  # header crudo
  "x_request_id": "req-abc",
  "data_id": "payment-456",
  "secret": "tu-webhook-secret-del-panel-mp",
  "max_age_seconds": 300  # opcional, anti-replay
}
# →
{
  "valid": true | false,
  "reason": null | "hmac_mismatch" | "expired_timestamp" | "missing_secret" | ...,
  "timestamp": 1742068800,
  "data_id": "payment-456"
}
```

**Algoritmo oficial Mercado Pago**:
1. Construye manifest: `id:<data_id>;request-id:<x_request_id>;ts:<ts>;`
2. HMAC-SHA256(manifest, secret) en hex debe igualar el `v1=...` del header
3. Opcional: rechaza si `ts` es más viejo que `max_age_seconds` (anti-replay)

### `mercadopago_get_payment`
Consulta un pago. Cache 2 min (status puede cambiar).

```python
{"payment_id": "12345"}
# →
{
  "id": 12345,
  "status": "approved",
  "status_description": "Pago aprobado y acreditado",
  "is_paid": true,           # ← campo derivado para conveniencia
  "is_terminal": true,
  "is_refundable": true,
  "transaction_amount": 1500.0,
  "currency_id": "MXN",
  "external_reference": "cot-123",  # ← tu mapeo interno
  "date_approved": "...",
  ...
}
```

### `mercadopago_list_payments`
Busca pagos por filtros. Útil para reconciliar.

```python
{
  "external_reference": "cot-123",
  "status": "approved",
  "fecha_desde": "2026-03-01T00:00:00.000-06:00",
  "fecha_hasta": "2026-03-31T23:59:59.000-06:00",
  "limit": 50
}
```

### `mercadopago_refund_payment`
Refund total o parcial. Sin `amount` → total.

```python
{"payment_id": "12345", "amount": 750.0}  # refund parcial
# →
{"id": 67890, "status": "approved", "amount": 750.0, ...}
```

Recordatorio fiscal: tras un refund debes emitir CFDI tipo E (Egreso) con `TipoRelacion=01` vinculado al CFDI original.

### `mercadopago_cancel_payment`
Cancela un pago en `status=pending`. No funciona en pagos ya aprobados (para eso usa refund).

### `mercadopago_get_preference`
Lee detalle de preferencia ya creada. Cache 15 min.

### `mercadopago_listar_catalogos`
Discovery sin red: payment_status, payment_status_detail, refund_status, subscription_status, webhook_topics, currency.

## Flujo crítico: payment link → CFDI automático

```
1. cliente paga vía init_point
   ↓
2. MP envía POST a tu notification_url con
   headers: x-signature, x-request-id
   query string: ?data.id=<PAYMENT_ID>&type=payment
   ↓
3. Tu webhook receiver llama mercadopago_validate_webhook_signature
   - Si valid=false → responde 200 OK (para que MP no reintente) pero NO procesa
   - Si valid=true → continúa
   ↓
4. Llama mercadopago_get_payment(data_id) para obtener detalle
   ↓
5. Si is_paid=true:
   - Busca tu external_reference en tu base interna
   - Construye payload CFDI con facturama_validar_payload_local
   - Si pasa: facturama_timbrar_cfdi
   - Notifica al cliente vía WhatsApp con el UUID
   ↓
6. Responde 200 OK al webhook (idempotente — si MP reintenta, no dupliques CFDI)
```

## Estados de pago (resumen)

| Status | Significado | is_paid | is_terminal | is_refundable |
|---|---|---|---|---|
| `pending` | Iniciado, no procesado | ❌ | ❌ | ❌ |
| `approved` | Aprobado y acreditado | ✅ | ✅ | ✅ |
| `authorized` | Autorizado, no capturado (TDC) | ❌ | ❌ | ✅ |
| `in_process` | En revisión antifraude | ❌ | ❌ | ❌ |
| `rejected` | Rechazado | ❌ | ✅ | ❌ |
| `cancelled` | Cancelado o expirado | ❌ | ✅ | ❌ |
| `refunded` | Reembolsado total | ❌ | ✅ | ❌ |
| `charged_back` | Contracargo bancario | ❌ | ✅ | ❌ |

## Modos de operación

| Estado | Cuándo | Comportamiento |
|---|---|---|
| **Real sandbox** | Token `TEST-...` | Llama API, sandbox URLs, sin cobros reales |
| **Real producción** | Token `APP_USR-...` | Llama API, cobros REALES |
| **Mock** | Sin token o `PLUGINS_MX_MOCK=1` | preference_id determinístico, pagos simulados |

## Bitácora

Cada `create_preference`, `refund_payment` se registra en `~/.local/share/plugins-mx/audit-log/mercadopago_mcp/YYYY-MM.jsonl`.

**external_reference y payment_id se hashean** con `Bitacora.hash_sensitive()` — no fugas de PII al log pero conserva capacidad de análisis.

## ⚠ Datos a verificar vigentes

- **Catálogos de estados** (`catalogos.py`): estables desde 2018+, pero validar contra https://www.mercadopago.com.mx/developers si surge un valor desconocido
- **Endpoints**: el cliente usa rutas estables; cambios MP requerirán ajuste
- **Algoritmo HMAC**: documentado por MP, estable

## Tests

```bash
cd mcp-servers
.venv/bin/python -m pytest mp_mercado_pago/tests -v
```

Cobertura actual: **75 tests** cubriendo:
- 12 tests de catálogos (status helpers, integridad cross-referencias)
- 22 tests de webhooks (firma válida, todos los failure modes, anti-replay, parse header con whitespace/orden invertido)
- 21 tests del cliente (mock determinístico, env detection, cache, bitácora con hashing)
- 20 tests end-to-end de los 9 tools del server
