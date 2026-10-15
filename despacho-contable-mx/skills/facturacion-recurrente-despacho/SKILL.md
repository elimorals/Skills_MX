---
name: facturacion-recurrente-despacho
description: Facturación recurrente del despacho a sus clientes por servicios contables (mensualidad típica $800-$5,000 MXN según tamaño). Emite CFDI G03 (gastos en general) cada mes 1, gestiona cobranza escalada, y reporta morosidad. Usar cuando el usuario diga facturar clientes despacho, mensualidad clientes, cobranza honorarios.
allowed-tools: Read, Write
---

# Facturación recurrente despacho

## Modelo

Cada cliente paga mensualidad fija. Día 1 del mes:
1. Emitir CFDI de ingreso al cliente (uso CFDI que indique el cliente; normalmente G03). Como aún no está cobrado: **método PPD, forma 99** y complemento de pago (REP) al cobrar, a más tardar el día 5 del mes siguiente. Usa PUE solo si se cobra en el mismo mes (ver skill `cfdi-emision` de `core-mexico`).
   - Retenciones si el cliente es persona moral: despacho PF en régimen 612 → 10% ISR + 2/3 del IVA; despacho PF en RESICO → 1.25% ISR + 2/3 del IVA; despacho PM → sin retención. El Total del CFDI resta las retenciones.
2. Enviar a su email/WA (WhatsApp solo con opt-in; ver `comunicacion-clientes-batch`)
3. Si no paga en 5 días: nivel 1 cobranza
4. D+15: nivel 2
5. D+30: pausar servicio + alerta crítica

## Output run mensual

```json
{
  "fecha_run": "2026-06-01",
  "clientes_activos": 47,
  "cfdis_emitidos": 47,
  "monto_facturado_mxn": "165000.00",
  "cobranza_iniciada": [],
  "alertas": [],
  "siguiente_corrida": "2026-07-01"
}
```
