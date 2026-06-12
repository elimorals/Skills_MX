---
name: dashboard-host
description: Dashboard mensual del Airbnb host. Muestra reservas, noches ocupadas, tasa ocupación, ingresos brutos, retenciones plataforma (Art. 113-A), neto recibido, ISH pagado, ranking en la zona, próximas reservas y status RAB CDMX. Usar cuando el usuario diga cómo va mi Airbnb, dashboard host, ocupación mes, ingresos hospedaje.
allowed-tools: Read, Write
---

# Dashboard Airbnb host

## Output

```
🏠 PROPIEDAD: Roma Norte (3 cuartos)
   Plataforma principal: Airbnb
   Status RAB CDMX: ✓ Registrado (RAB-XXXXX)

📅 Junio 2026:
   Noches reservadas: 22 de 30
   Tasa ocupación: 73%
   Promedio tarifa/noche: $1,850

💰 Ingresos:
   Bruto:              $40,700
   Comisión Airbnb:    ─$5,698 (14%)
   Retención ISR:      ─$1,628 (4%)
   Retención IVA:      ─$3,256 (8%)
   ISH CDMX 3.5%:      ─$1,425
   🟢 Neto recibido:    $28,693

📊 vs mes pasado: +12%
🎯 Próximas reservas: 3 (julio, $5,500 confirmados)
⚠ Pendiente: presentar ISH ante Tesorería CDMX
```

## Data sources

- Panel Airbnb (manual export CSV o panel host)
- Tracker local de reservas
- Tracker fiscal local
