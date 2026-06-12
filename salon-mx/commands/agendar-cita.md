---
description: Agenda una cita en el salón con estilista, servicio, hora y recordatorios automáticos WhatsApp 24h y 2h antes.
argument-hint: "[cliente, servicio, estilista (opcional), fecha y hora]"
allowed-tools: Read, Write, Edit
---

# /salon:agendar-cita

Agenda una cita: $ARGUMENTS

## Lo que hace

1. Invoca skill `agenda-citas-salon` con los datos del cliente y servicio.
2. Verifica `servicios-tarifario` para confirmar duración y precio.
3. Aplica política anti no-show (depósito si cliente con histórico):
   - 1ra cita / sin no-shows: sin depósito
   - 1 no-show: depósito 30%
   - 2+ no-shows: depósito 100%
4. Verifica buffer entre citas del estilista (10-20 min según servicio).
5. Programa recordatorios WhatsApp: 24h, 2h, 30min antes.
6. Confirma cita por WhatsApp al cliente.

## Output esperado

```
✓ Cita agendada — C-2026-0042

Cliente:        Ana Martínez (+52555...)
Estilista:      Carla
Servicio:       Corte mediano + tinte completo
Duración:       150 min
Inicio:         2026-03-15 14:00
Total estimado: $1,450 MXN
Depósito:       NO requerido (sin no-shows histórico)

Recordatorios programados:
  • 2026-03-14 14:00 (24h antes)
  • 2026-03-15 12:00 (2h antes)
  • 2026-03-15 13:30 (30min antes)

Confirmación WhatsApp enviada ✓
```
