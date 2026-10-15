---
name: dashboard-notaria-mes
description: Dashboard mensual para notario(a) con escrituras otorgadas por tipo, ingresos por honorarios e IVA, impuestos calculados y enterados por la notaría (ISAI/ISABI, ISR por enajenación Art. 126 LISR, pago estatal Art. 127), avisos antilavado LFPIORPI pendientes, escrituras pendientes de inscripción en el RPP y conciliación del protocolo físico contra el registro digital. Usar cuando el usuario diga dashboard notaria, escrituras del mes, ingresos notaria, impuestos por enterar notaría.
allowed-tools: Read, Write
---

# Dashboard notaría mes

## Output (ejemplo)

```
⚖️  NOTARÍA 67 — Junio 2026

📜 Escrituras otorgadas: 47
  • Compraventa:        18 (38%)
  • Testamento:         12
  • Poder general:       8
  • Sociedad:            5
  • Sucesión:            3
  • Hipoteca:            1

💰 Honorarios:          $890,000 MXN
   IVA trasladado 16%:  $142,400 MXN

🏛 Impuestos a cargo de la notaría (por enterar dentro de plazo):
   ISAI/ISABI (18 compraventas): $1,250,000 MXN — 12 enterados, 6 pendientes
   ISR enajenación (Art. 126) + estatal 5% (Art. 127): 6 operaciones gravadas,
     12 con exención casa habitación (Art. 93 fr. XIX) — plazo: 15 días desde la firma
   ⚠ 2 pagos de ISR vencen esta semana

🛡 Antilavado (LFPIORPI):
   Expedientes de identificación completos: 18/18
   Avisos UIF por presentar (día 17 del mes siguiente): 4

📋 Estado RPP:
  Inscritas:            32
  Pendientes:           12
  Rechazadas:            3 (revisar)

📚 Conciliación protocolo:
  Último número asentado (protocolo): 12,345
  Último número en sistema digital:   12,345 ✓
```

Cálculos: 18/47 = 38%; IVA = 890,000 × 16% = 142,400; ISAI e ISR solo en operaciones traslativas (aquí las 18 compraventas: 12 + 6 ISAI; 6 gravadas + 12 exentas de ISR).

## Alertas que debe generar

- ISR Art. 126/127 con plazo de 15 días por vencer
- ISAI con plazo local por vencer (según ley de cada entidad)
- Avisos LFPIORPI pendientes al día 10 del mes (vencen el 17); umbral vigente: **verificar** tras la reforma DOF 16-07-2025
- Escrituras rechazadas por el RPP

## Data sources

- `registro-escrituras-tipos` (registro maestro)
- Acuses de DeclaraNOT y de pagos estatales
