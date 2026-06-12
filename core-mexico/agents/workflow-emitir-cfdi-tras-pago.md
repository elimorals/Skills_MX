---
name: workflow-emitir-cfdi-tras-pago
description: Workflow que formaliza la cola del webhook receiver para emitir CFDI tras recibir confirmación de pago (Stripe/MP/Conekta). Valida que el pago efectivamente entró al banco, identifica cliente + RFC, construye payload CFDI, timbra, envía CFDI al cliente. Usar cuando el usuario diga emitir cfdi automatico pago, workflow pago a cfdi, automatizar facturacion pagos.
allowed-tools: Read, Write
---

# Workflow emitir CFDI tras pago

## Trigger

- Webhook `mercadopago/conekta/stripe` recibe evento `payment.succeeded`
- Handler valida firma y encola
- Este workflow procesa la cola

## Fases

### 1. Validar pago real
- Cruce con extracto bancario (`mp_bancos_mx`)
- Si modo mock: confirmar dummy
- Si NO se confirma en 24h: alerta + no emitir CFDI

### 2. Identificar cliente
- Email/teléfono → directorio clientes
- Si no existe: crear placeholder + flag "validar datos"
- Si tiene RFC: usar para CFDI normal
- Si no: emitir XAXX010101000 (público en general)

### 3. Construir CFDI
- Uso: G03 (servicios) o el específico según producto
- Forma pago: 03 (transferencia) / 04 (tarjeta) según procesador
- Método: PUE (pago en una sola exhibición)

### 4. Timbrar
- `mp_facturama_extendido.timbrar_cfdi`
- Si falla: reintentar 3x backoff
- Si persiste falla: alerta crítica

### 5. Notificar cliente
- Email con XML + PDF
- WhatsApp opcional con link de descarga
- Persistir en backup local

### 6. Output

```json
{
  "workflow": "emitir_cfdi_tras_pago",
  "payment_id": "...",
  "monto_mxn": "...",
  "cliente_rfc_hash": "...",
  "cfdi_uuid": "...",
  "tiempo_total_ms": 1850,
  "exitoso": true
}
```

## Pre-conditions

- Webhook receiver funcionando
- `mp_facturama_extendido` con credenciales reales
- Cliente en directorio o XAXX por default

## Hook que se activa

`pre-timbrado-validation.sh` (PreToolUse) — bloquea si RFC mal, totales raros, etc.
