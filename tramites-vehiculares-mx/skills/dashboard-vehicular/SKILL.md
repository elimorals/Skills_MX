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
   Próxima: 2026-09-01 al 2026-10-31 (engomado rojo, terminación 4)

💰 Refrendo + Tenencia 2026:
   ✓ Pagado 2026-01-12

🚓 Multas vigentes (EdoMex):
   ⚠ 2 multas pendientes — $1,250 MXN total
   • 2026-04-12: estacionar en lugar prohibido $750
   • 2026-05-20: velocidad +20% $500
   → /vehiculos:multas para pagar

📅 Próximos vencimientos:
   • Verificación: 2026-10-31
   • Refrendo/subsidio tenencia 2027: primer trimestre (fecha exacta por confirmar)
```

## Data sources

- Tracker local placas: `~/.local/share/plugins-mx/placas-vehiculos.jsonl`
- Multas: `mp_multas_vehiculares_mx.multas_consultar_por_placa` (CDMX, EdoMex, Jalisco, NL, San Pedro). Entrega a humano: si devuelve `requiere_humano: true`, muestra "sin consultar" con la URL, nunca "sin multas".
- Verificación: `mp_verificacion_vehicular_mx.verificacion_proximo_periodo` (cálculo local) y `verificacion_consultar_estatus` (CAPTCHA en CDMX → handoff).
- Refrendo/tenencia: `mp_tenencia_mx.tenencia_calcular` (montos 2026 de prensa, confianza media/baja).
- Robo/registro: `mp_repuve` (entrega a humano).

Cada bloque del dashboard indica su fuente: `consultado`, `capturado por el usuario` o `pendiente (handoff)`. El semáforo rojo (≤ 7 días) solo se calcula con fechas confirmadas.

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
