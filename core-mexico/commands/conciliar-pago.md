---
description: Workflow de conciliación de pago entrante (webhook MP/Conekta o clave SPEI) con CFDI emitido, emisión de REP si es PPD, y notificación al cliente. Despacha el subagent workflow-pago-conciliacion.
argument-hint: "[fuente del pago: webhook MP, webhook Conekta, clave SPEI manual, o payment_id]"
allowed-tools: Read, Write, Edit, Bash, Task
---

# /core:conciliar-pago

Concilia un pago entrante con la factura emitida: $ARGUMENTS

## Lo que hace

1. **Valida la señal del pago** según fuente:
   - Webhook MP: `mp_mercado_pago.validate_webhook` + `get_payment`
   - Webhook Conekta: `mp_conekta.conekta_validate_webhook` + `conekta_get_order`
   - SPEI manual: `mp_banxico_cep.consultar_pago_por_clave`
2. **Hace match con el CFDI emitido**:
   - Por external_reference si está disponible
   - Por heurística (mismo total, mismo RFC, fecha ±5 días) si no
3. **Emite REP si el CFDI original es PPD** (comprobante tipo P).
4. **Actualiza bitácora** del CFDI: pago_conciliado_at, pago_origen, etc.
5. **Notifica al cliente** vía WhatsApp con template "pago confirmado".

## Cómo lo ejecuta

Despacha al subagent `workflow-pago-conciliacion` (en `core-mexico/agents/`) para procesar el evento de forma aislada.

## Cuándo usar este comando

- Recibiste un webhook de pasarela de pagos
- El cliente avisó por WhatsApp "ya te pagué" con clave SPEI
- Necesitas reprocesar un pago que quedó pendiente
- Batch al cierre de mes contra extracto bancario

## Output esperado

```
✅ Pago conciliado
  CFDI original: F-2026-0042 (UUID ABCD-...)
  Monto recibido: $116,000 MXN (PPD completo)
  REP emitido: P-2026-0042 (UUID EFGH-...)
  Cliente notificado por WhatsApp: ✓
```

## Modo simulado

Sin credenciales reales: el workflow simula validación de firma + emisión REP con UUIDs sintéticos. Marca `simulated: true` en cada paso.
