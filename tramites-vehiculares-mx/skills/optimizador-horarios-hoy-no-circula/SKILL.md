---
name: optimizador-horarios-hoy-no-circula
description: Optimiza la planificación semanal del vehículo bajo el programa Hoy No Circula (CDMX + Estado de México zona conurbada). Genera calendario "qué día no circula tu vehículo + restricciones extras por contingencia ambiental". Útil para conductores con compromisos diarios que necesitan saber qué día NO usar su auto. Usar cuando el usuario diga hoy no circula, no circula mi auto, calendario restriccion.
allowed-tools: Read, Write
---

# Optimizador Hoy No Circula

## Reglas (CDMX/Edo Méx zona)

Días por holograma + último dígito:

| Holograma | Días que NO circula |
|---|---|
| 0 / 00 / Exento | Ninguno |
| 1 — dígito 5,6 | Lunes + 1er sábado de mes |
| 1 — dígito 7,8 | Martes + 2do sábado |
| 1 — dígito 3,4 | Miércoles + 3er sábado |
| 1 — dígito 1,2 | Jueves + 4to sábado |
| 1 — dígito 9,0 | Viernes + 5to sábado (si lo hay) |
| 2 — todos los dígitos | Días asignados según holograma 1 + sábados extra |

## Contingencia ambiental

Si Fase 1 o 2 declarada:
- Hologramas 1-2 con restricciones extras (incluso días que normalmente circularían)
- Vehículos con verificación 0 / exentos siempre circulan

## Output

```
🚗 TU AUTO: ABC-1234 (Holograma 1, dígito 4)

📅 Semana próxima:
  Lun 16:  ✓ Circula
  Mar 17:  ✓ Circula
  Mié 18:  ✗ NO CIRCULA (mié dígito 3-4)
  Jue 19:  ✓ Circula
  Vie 20:  ✓ Circula
  Sáb 21:  ✓ Circula (no es 3er sábado este mes)
  Dom 22:  ✓ Circula

📋 Próximo 3er sábado: 2026-07-19 → tampoco circula
```
