---
description: Agenda vacuna(s) para una mascota considerando esquema vigente (cachorro/adulto), historial previo y disponibilidad. Programa recordatorios WA.
argument-hint: "[id mascota o nombre, vacuna(s) deseadas]"
allowed-tools: Read, Write, Edit
---

# /vet:agendar-vacuna

Agenda vacuna: $ARGUMENTS

## Lo que hace

1. Lee expediente clínico de la mascota (skill `expediente-clinico-mascota`).
2. Valida esquema vigente y próximas vacunas pendientes (skill `vacunacion-calendario`).
3. Verifica alergias y reacciones previas a vacunas.
4. Agenda fecha con MVZ disponible.
5. Programa recordatorios WhatsApp: 30 días, 7 días, 24h antes (skill `recordatorios-pet-wa`).
6. Confirma con el tutor por WhatsApp.

## Output esperado

```
✓ Vacuna agendada — Luna (PET-2026-001234)

Vacuna:        Multivalente DAPP-L (refuerzo anual)
Marca sugerida: Nobivac DHPPi-L4
Fecha:         2026-06-15 11:00
MVZ:           Dr. Demo Cert. 12345
Precio:        $380 MXN

Recordatorios WA programados:
  • 2026-05-16 (30d antes)
  • 2026-06-08 (7d antes)
  • 2026-06-14 (24h antes)

Alertas:
  • No tiene reacciones adversas previas a esta vacuna
  • Compatible con su medicación actual
```
