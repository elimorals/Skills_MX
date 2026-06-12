---
description: Genera timeline operativo para boda desde D-365 hasta D+30 con hitos críticos por etapa.
argument-hint: "[fecha del evento, modalidad: full / day-of]"
allowed-tools: Read, Write, Edit
---

# /wedding:timeline-boda

Genera timeline: $ARGUMENTS

## Lo que hace

Skill `timeline-evento` produce Gantt detallado con hitos por etapa:
- D-365 a D-180: decisiones estructurales
- D-180 a D-90: cierre proveedores
- D-90 a D-30: confirmaciones y pruebas
- D-30 a D-7: finalización
- D-7 a D-1: ensayo y setup
- D-0: día del evento
- D+1 a D+30: post-evento
