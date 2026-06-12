---
description: Manda recordatorio personalizado a clientes con cita próxima (24h o 2h antes) o reactivación a clientes que se atrasaron (no-show recovery).
argument-hint: "[tipo: '24h', '2h', '30min', 'recovery']"
allowed-tools: Read, Write, Edit
---

# /salon:recordatorio-no-show

Manda recordatorios WhatsApp: $ARGUMENTS

## Lo que hace

### Modo 24h, 2h, 30min
Identifica citas próximas y envía template aprobado WhatsApp Business:
- `recordatorio_24h`: confirmación
- `recordatorio_2h`: link a Google Maps + opción modificar
- `recordatorio_30min`: "llegando pronto" + estatus

### Modo recovery
Identifica clientes que no llegaron (no-show) o que se atrasaron (>X días sin visitar) y manda mensaje de reactivación.

## Output esperado

```
✓ Recordatorios enviados — 2026-03-14

Para citas mañana (24h):
  • Ana M.    → "recordatorio_24h"  ✓ entregado
  • Carlos R. → "recordatorio_24h"  ✓ entregado
  • Sofía L.  → "recordatorio_24h"  ✓ entregado

Recovery no-shows últimos 7 días:
  • Pedro J.  → "regresa_descuento_15"  ✓ entregado
  • María G.  → "ya_no_te_vemos"         ✓ entregado

3 clientes confirmaron, 2 sin respuesta.
```
