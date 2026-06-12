---
name: dashboard-vehicular
description: Dashboard integral por vehículo del usuario (1 o varios). Muestra multas pendientes por entidad, status verificación vehicular (último periodo + próximo), refrendo del año pagado o pendiente, tenencia (si aplica al estado), vigencia de placas, y semáforo de urgencia (rojo si hay deadline ≤ 7 días). Útil al inicio del mes y antes de viajes interurbanos. Usar cuando el usuario diga status auto, dashboard vehículo, cómo está mi carro, obligaciones vehículo. NO usar para reparaciones (talleres-mx).
allowed-tools: Read, Write
---

# Dashboard vehicular — México

## Trigger

- "¿cómo va mi auto?"
- "status placas"
- Antes de viajar (asegurarse que todo está OK)

## Output

```
🚗 PLACA: ABC-1234 (Honda Civic 2020)
   Estado registro: EdoMex

📋 Verificación vehicular:
   Última: 2026-03-15 ✓ HOLOGRAMA 1
   Próxima: 2026-09-01 al 2026-10-31 (en 90 días)

💰 Refrendo + Tenencia 2026:
   ✓ Pagado 2026-01-12

🚓 Multas vigentes (EdoMex):
   ⚠ 2 multas pendientes — $1,250 MXN total
   • 2026-04-12: estacionar en lugar prohibido $750
   • 2026-05-20: velocidad +20% $500
   → /vehiculos:multas para pagar

📅 Próximos vencimientos:
   • Refrendo 2027: 31 enero 2027
   • Verificación: 2026-09-30
```

## Data sources

- Tracker local placas: `~/.local/share/plugins-mx/placas-vehiculos.jsonl`
- MCPs: `mp_cdmx_municipal`, `mp_edomex_municipal`, `mp_monterrey_municipal`
- Calendarios verificación por estado (catálogo local)

## Schema tracker

```json
{
  "placa": "ABC-1234",
  "marca_modelo": "Honda Civic 2020",
  "entidad_registro": "edomex",
  "ultimo_holograma": "1",
  "ultima_verificacion": "2026-03-15",
  "refrendo_pagado_anios": [2024, 2025, 2026]
}
```
