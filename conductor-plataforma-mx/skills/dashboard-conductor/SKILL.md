---
name: dashboard-conductor
description: Dashboard semanal/mensual del conductor de plataforma. Muestra ingresos brutos por plataforma (Uber, DiDi, Cabify, InDriver), comisiones cobradas, retenciones aplicadas (2.1% ISR Art. 113-A LISR + 8% IVA Art. 18-J LIVA), neto recibido, viajes realizados, horas activas, y rating actual. Útil al cierre de cada semana para reconciliar. Usar cuando el usuario diga cómo me fue esta semana, dashboard chofer, cuánto gané en Uber, ingresos plataforma, ganancia semana, resumen semanal. NO usar para fines fiscales formales (eso es calculo-fiscal-conductor).
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
   Retenciones SAT:    ─$  611 (ISR 2.1% = $127.05 Art. 113-A LISR + IVA 8% = $484.00 Art. 18-J LIVA)
🟢 Neto recibido:       $4,229

⏰ Horas activas: 35
   Promedio por hora:  $120.83 neto

🎯 Comparativa:
   • Semana pasada: $4,180 (+$49, +1.2%)
   • Promedio últimas 4: $4,290 (−$61, −1.4%)
```

## Data sources

- Tracker manual o CSV/resumen exportado de cada plataforma (fuente principal)
- `mp_didi_partners`: DiDi no publica API para conductores; con credenciales devuelve `ConfigError` → pedir el resumen de la app al usuario
- `mp_cabify_business` es para **empresas que piden viajes** (estimar, pedir, consultar), no para ingresos del conductor: no usarlo aquí
- Uber, inDrive: sin MCP; login manual del conductor a su panel

## Schema tracker

```json
{
  "semana": "2026-W24",
  "plataforma": "uber",
  "ingresos_brutos_mxn": "4200.00",
  "comision_plataforma_mxn": "840.00",
  "retencion_isr_mxn": "88.20",
  "retencion_iva_mxn": "336.00",
  "neto_mxn": "2935.80",
  "viajes": 38,
  "horas_activas": 22,
  "rating": 4.8
}
```

## ⚠ Compliance

- Hashear datos del conductor en logs
- NO almacenar contraseñas de plataformas (manual login)
