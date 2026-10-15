---
name: dashboard-host
description: Dashboard mensual del Airbnb host. Muestra reservas, noches ocupadas, tasa ocupación, ingresos brutos, comisión de la plataforma, retenciones de ISR e IVA (Art. 113-A LISR / Art. 18-M LIVA), neto depositado, ISH (quién lo entera), comparativo vs mes anterior, próximas reservas y estatus del registro de anfitriones CDMX. Usar cuando el usuario diga cómo va mi Airbnb, dashboard host, ocupación mes, ingresos hospedaje.
allowed-tools: Read, Write
---

# Dashboard Airbnb host

## Output (ejemplo ilustrativo, departamento completo en CDMX vía Airbnb)

```
🏠 PROPIEDAD: Roma Norte (3 cuartos)
   Plataforma principal: Airbnb
   Padrón anfitriones CDMX: ✓ Inscrito (folio XXXXX)

📅 Junio 2026:
   Noches reservadas: 22 de 30
   Tasa ocupación: 73.3%
   Promedio tarifa/noche: $1,850

💰 Ingresos:
   Hospedaje (sin IVA):          $40,700.00
   IVA trasladado 16%:           +$6,512.00
   Comisión Airbnb 14% + IVA:    −$6,609.68
   Retención ISR 4% (113-A II):  −$1,628.00
   Retención IVA 8% (18-M):      −$3,256.00
   🟢 Depósito estimado:          $35,718.32

   ISH CDMX 5%: $2,035.00 → lo cobra Airbnb al huésped y lo entera; no sale de tu depósito
   IVA no retenido: $3,256.00 → lo enteras tú, salvo que optes por pago definitivo (ingresos ≤ $300,000/año)

📊 vs mes pasado: +12%
🎯 Próximas reservas: 3 (julio, $5,500 confirmados)
```

Cálculos: 22 × $1,850 = $40,700; 22/30 = 73.3%; comisión 40,700 × 14% = 5,698 + IVA 911.68; ISR 40,700 × 4%; IVA retenido = 50% de 6,512; ISH 40,700 × 5%.

La comisión real depende de tu esquema (tarifa dividida o solo anfitrión): tómala de tu reporte de ganancias. Las cifras oficiales son las del reporte de pagos y del CFDI de retenciones que emite la plataforma; este tablero es una estimación.

## Data sources

- Panel Airbnb (export CSV de ganancias)
- CFDI de retenciones mensual de la plataforma
- Tracker local de reservas y tracker fiscal
- Tasas ISH: `mcp-servers/shared/ish_mx.py` (ver skill `calculador-ish-por-estado`)
