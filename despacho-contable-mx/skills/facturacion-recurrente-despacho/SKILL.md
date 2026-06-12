---
name: facturacion-recurrente-despacho
description: Facturación recurrente del despacho a sus clientes por servicios contables (mensualidad típica $800-$5,000 MXN según tamaño). Emite CFDI G03 (gastos en general) cada mes 1, gestiona cobranza escalada, y reporta morosidad. Usar cuando el usuario diga facturar clientes despacho, mensualidad clientes, cobranza honorarios.
allowed-tools: Read, Write
---

# Facturación recurrente despacho

## Modelo

Cada cliente paga mensualidad fija. Día 1 del mes:
1. Emitir CFDI G03 al cliente
2. Enviar a su email/WA
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
