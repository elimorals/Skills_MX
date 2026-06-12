---
name: workflow-pago-conciliacion
description: Orquesta la conciliación de un pago entrante con una factura emitida (webhook MP/Conekta o clave SPEI manual → match con CFDI → emitir Recibo Electrónico de Pago si es PPD → notificar cliente). Despachar cuando el usuario diga "concilia este pago", "me llegó un SPEI, márcalo como pagado", "el cliente me pagó la factura X", "procesar webhook de Mercado Pago/Conekta". Subagent porque coordina 3-5 MCPs y genera mucho ruido.
tools: Read, Write, Bash, Grep
---

# Workflow: Conciliación de pago entrante

Convierte una señal de pago (webhook de pasarela o clave SPEI captada manualmente) en una **conciliación contable completa**: match con CFDI emitido, emisión de REP si es PPD, actualización de bitácora y notificación al cliente.

## Cuándo te despachan

- Llegó webhook de Mercado Pago / Conekta y el contexto principal necesita procesarlo
- El cliente avisa por WhatsApp "ya te pagué" con clave de rastreo SPEI
- Mensual: cerrar matching de todos los pagos del mes
- Después de subir extracto bancario: cruzar contra CFDIs emitidos PPD

## Inputs aceptados

El subagent acepta cualquiera de estos:

1. **Webhook signed payload** de MP o Conekta (validar firma primero)
2. **Clave de rastreo SPEI + monto + fecha** (manual desde WhatsApp del cliente)
3. **Lista de movimientos bancarios** (CSV o JSON) para batch matching
4. **Payment link ID** específico para verificar status

## Fases del workflow

### Fase 1: Validación del evento de pago

Según el input:

**Webhook MP**:
- `mp_mercado_pago` tool `validate_webhook` con headers + payload + secret
- Si `valid: false` → abortar (intento de spoofing)
- Extraer `payment_id` del body
- `mp_mercado_pago.get_payment(payment_id)` → status debe ser `approved`

**Webhook Conekta**:
- `mp_conekta.conekta_validate_webhook` con headers + payload + secret
- Si `valid: false` → abortar
- Extraer `data.object.id` del body (charge_id u order_id)
- `mp_conekta.conekta_get_order(order_id)` → payment_status `paid`

**Clave SPEI manual**:
- `mp_banxico_cep.banxico_cep_parsear_clave_rastreo(clave)` → emisor probable
- `mp_banxico_cep.banxico_cep_consultar_pago_por_clave(clave, fecha, monto)` → confirmar SPEI real

### Fase 2: Match con CFDI emitido

Buscar el CFDI correspondiente:

1. Si el pago tiene `external_reference` (MP) o `metadata.invoice_id` (Conekta): match directo por folio.
2. Si no: match heurístico:
   - Mismo total (con tolerancia $1 MXN por redondeo)
   - Mismo RFC receptor (si conocido por el panel cliente del comercio)
   - Fecha del pago dentro de ±5 días de la emisión del CFDI
3. Si hay **múltiples candidatos**: presentar lista al usuario para elegir, NO autoresolver.
4. Si hay **cero candidatos**: marcar pago como "huérfano" para revisión manual.

### Fase 3: Emitir REP si es PPD

Si el CFDI original tiene `MetodoPago=PPD`:

1. Construir payload del **Comprobante tipo P** (Recibo Electrónico de Pago):
   - Relación al UUID del CFDI original
   - Pago con FormaPago real (03 transferencia, 02 cheque, etc.)
   - Monto pagado (puede ser parcial — generar otro REP cuando llegue el resto)
   - Total pagado en moneda original + TC si es multimoneda
2. Invocar `mp_facturama_extendido.timbrar_cfdi` con type=P
3. Capturar UUID del REP
4. Vincular: anotar UUID del REP en bitácora del CFDI original

Si el CFDI original es `MetodoPago=PUE`: **no se emite REP** (PUE ya implica pagado).

### Fase 4: Actualización de bitácora

Registrar en bitácora del CFDI:
- `pago_conciliado_at`: timestamp
- `pago_origen`: "mercado_pago" | "conekta" | "spei_manual"
- `pago_payment_id` o `clave_rastreo`
- `pago_total`: monto recibido
- `pago_rep_uuid`: si se emitió REP
- `pago_status`: "PAGADO_COMPLETO" | "PAGADO_PARCIAL" | "PENDIENTE"

### Fase 5: Notificación al cliente

Si hay template aprobado para "pago confirmado":
- Variables: nombre, folio del CFDI original, monto pagado, link al REP (si aplica)
- Enviar via MCP WhatsApp

Si NO hay template:
- Generar texto sugerido para envío manual

### Fase 6: Reporte ejecutivo

```json
{
  "fase_validacion": {
    "fuente": "mercado_pago_webhook",
    "firma_valida": true,
    "payment_id": "1234567890",
    "status_pago": "approved",
    "monto_recibido": 116000.00,
    "moneda": "MXN"
  },
  "fase_match": {
    "cfdi_uuid_original": "ABCD-...",
    "folio_original": "F-2026-0042",
    "metodo_pago_original": "PPD",
    "match_score": "EXACTO",
    "criterio": "external_reference"
  },
  "fase_rep": {
    "rep_emitido": true,
    "rep_uuid": "EFGH-...",
    "rep_folio": "P-2026-0042",
    "tipo": "PAGO_COMPLETO"
  },
  "fase_notificacion": {
    "enviado": true,
    "template": "pago_confirmado_v2"
  },
  "estado_final": "PAGO_CONCILIADO_COMPLETO"
}
```

## Manejo de errores

| Caso | Acción |
|---|---|
| Webhook con firma inválida | Abortar inmediatamente. NO procesar el evento (probable spoofing). |
| Pago aprobado pero CFDI no encontrado | Marcar como pago huérfano. Notificar al usuario para resolver manualmente. |
| Múltiples CFDIs candidatos | Presentar lista al usuario, no auto-resolver. |
| CFDI original cancelado | Alertar — el pago se recibió pero el CFDI ya no es válido. Devolución? |
| Monto del pago ≠ monto del CFDI | Si es parcial: emitir REP parcial. Si es exceso: notificar al usuario para devolución. |
| PAC falla al timbrar REP | Registrar pago como conciliado pero REP pendiente. Reintento manual. |
| WhatsApp falla | El pago queda conciliado de todos modos. Usuario envía manualmente. |

## Por qué subagent

- Webhook payloads son verbosos (a veces 5-10KB JSON)
- Validación de firma genera muchas operaciones criptográficas
- Match heurístico puede consultar múltiples CFDIs candidatos
- El usuario solo necesita "se concilió, aquí está el REP UUID"

## Mock-friendly

Cuando MCPs corren en mock:
- Webhook validation siempre `valid: true` con firmas conocidas
- `get_payment` retorna approved con monto sintético
- REP se emite con UUID sintético
- Bitácora se escribe pero marcada `simulated: true`

El workflow detecta y reporta el modo simulado en el output final.
