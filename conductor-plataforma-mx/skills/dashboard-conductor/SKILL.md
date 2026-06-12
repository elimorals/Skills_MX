---
name: dashboard-conductor
description: Dashboard semanal/mensual del conductor de plataforma. Muestra ingresos brutos por plataforma (Uber, DiDi, Cabify, InDriver), comisiones cobradas, retenciones aplicadas (8% ISR + 8% IVA art. 113-A LISR), neto recibido, viajes realizados, horas activas, y rating actual. Útil al cierre de cada semana para reconciliar. Usar cuando el usuario diga cómo me fue esta semana, dashboard chofer, ingresos plataforma, ganancia semana. NO usar para fines fiscales formales (eso es calculo-fiscal-conductor).
allowed-tools: Read, Write
---

# Dashboard conductor plataformas

## Output ejemplo

```
🚗 RESUMEN SEMANA — 2026-06-08 al 2026-06-14

📊 Ingresos por plataforma:
  Uber           $4,200   38 viajes  4.8★
  DiDi           $1,850   18 viajes  4.7★
  Cabify         $   0    0 viajes
  InDriver       $   0    0 viajes

💵 Total bruto:        $6,050
   Comisión plataforma: ─$1,210 (20%)
   Retenciones SAT:    ─$  484 (8% ISR + 8% IVA del 50% gravable)
🟢 Neto recibido:       $4,356

⏰ Horas activas: 35
   Promedio por hora:  $124.46 neto

🎯 Comparativa:
   • Semana pasada: $4,180 (+$176, +4.2%)
   • Promedio últimas 4: $4,290 (+$66, +1.5%)
```

## Data sources

- Tracker manual o CSV exportado de cada plataforma
- `mp_cabify_business` (parcial, solo empresas)
- Plataformas mayores (Uber, DiDi) requieren login manual al panel conductor

## Schema tracker

```json
{
  "semana": "2026-W24",
  "plataforma": "uber",
  "ingresos_brutos_mxn": "4200.00",
  "comision_plataforma_mxn": "840.00",
  "retencion_isr_mxn": "168.00",
  "retencion_iva_mxn": "168.00",
  "neto_mxn": "3024.00",
  "viajes": 38,
  "horas_activas": 22,
  "rating": 4.8
}
```

## ⚠ Compliance

- Hashear datos del conductor en logs
- NO almacenar contraseñas de plataformas (manual login)
