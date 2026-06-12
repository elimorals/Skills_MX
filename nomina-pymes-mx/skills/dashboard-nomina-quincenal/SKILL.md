---
name: dashboard-nomina-quincenal
description: Dashboard quincenal de nómina con resumen total empleados activos, sueldos brutos, retenciones (ISR + IMSS + INFONAVIT + alimentaria), pendientes pago, alertas (empleados sin RFC, CFDIs sin timbrar, vacaciones próximas a expirar). Útil al cierre de cada quincena antes de dispersar pagos. Usar cuando el usuario diga dashboard nomina, resumen quincena, status empleados patronal.
allowed-tools: Read, Write
---

# Dashboard nómina quincenal

## Output

```
📋 NÓMINA — Quincena 11 de 2026 (01-15 jun)

👥 Empleados:
  Activos:                  28
  Bajas mes:                 1 (José M. - 2026-06-10)
  Altas mes:                 2 (Ana T., Carlos R.)

💰 Sueldos brutos:        $385,400 MXN
   ISR retenido:          $ 42,180
   IMSS obrero:           $ 9,150
   INFONAVIT (descuentos): $ 5,830
   Alimentarias:           $ 8,200
   Otros descuentos:       $   650
   ─────────────────────────────
   Neto a pagar:          $319,390

📊 Patrón (cuotas patronales este mes):
   IMSS patronal:        $ 38,540
   INFONAVIT 5%:         $ 19,270
   Riesgo trabajo:       $  4,800
   ─────────────────────────────
   Total patronal:       $ 62,610

🎯 Costos totales nómina: $447,950

⚠ Alertas:
  • 2 empleados sin RFC capturado — bloquear CFDI
  • 1 vacaciones por vencer (Juan P. - 5 días disponibles, vence 2026-12-31)
  • Aguinaldo Q4: empezar provisión mensual ($X/mes)
```

## Métricas accionables

- **Costo patronal vs sueldo bruto** (~30% típico)
- **Rotación**: bajas/altas mes
- **Cumplimiento CFDI**: % timbrados antes del cierre
- **Provisión aguinaldo**: $X reservado vs requerido fin de año
