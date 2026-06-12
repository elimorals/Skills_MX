---
description: Cierre del día — consolida ventas, servicios, propinas, productos. Calcula totales por estilista. Detecta huecos del día. Genera reporte ejecutivo.
argument-hint: "[fecha opcional, default hoy]"
allowed-tools: Read, Write, Edit
---

# /salon:cierre-dia-salon

Cierra el día del salón: $ARGUMENTS

## Lo que hace

1. **Consolida servicios completados** del día (vs agenda planeada).
2. **Detecta no-shows + walk-ins** atendidos.
3. **Calcula totales** por estilista (servicios + propinas + productos).
4. **Identifica huecos** desperdiciados.
5. **Genera reporte de cierre** ejecutivo.

## Output esperado

```
✓ Cierre día — 2026-03-15

Ventas brutas:        $24,800 MXN
Productos retail:      $2,300 MXN
Propinas registradas:  $1,750 MXN
─────────────────────────────────
Total cobrado:        $28,850 MXN

Servicios completados: 38 / 42 agendados (90%)
No-shows:               3 ($1,250 perdidos)
Walk-ins atendidos:     2 ($900 ganados)

Por estilista:
  Carla:   18 servicios, $9,800   (+$650 propinas)
  Ana:     12 servicios, $7,200   (+$520 propinas)
  Sofía:    8 servicios, $5,300   (+$580 propinas)

Huecos del día: 4 (90 min total)
Tasa ocupación: 0.78 (target > 0.80)

Alertas:
  • 3 no-shows hoy — revisar política depósitos
  • Sofía con tiempo libre 14:00-15:30 → ofrecer walk-ins
```
