---
name: renovacion-vigencias-migra
description: Gestión proactiva de renovaciones de documentos migratorios (residencia temporal cada año, cambio temporal → permanente cuando aplicable, FMM en cruces). Alertas 90 días antes del vencimiento (renovación INM tarda 30-60d, no esperar al último día). Usar cuando el usuario diga vence mi residencia, renovar visa, renovacion migratoria.
allowed-tools: Read, Write
---

# Renovación vigencias migratorias

## Alertas escalonadas

| Días para vencer | Acción |
|---|---|
| > 90 días | Tracker informativo |
| 90 días | 🟡 Iniciar renovación |
| 60 días | 🟠 Urgente — debiste haber empezado |
| 30 días | 🔴 Crítico |
| 0 días | ⛔ EN RIESGO MULTA + irregular |
| Vencida | Multa $5,400+ MXN + regularización |

## Renovaciones

- **Temporal 1er año → 2do año**: documentación reducida vs inicial
- **Temporal 3er año → permanente**: si cumple 4 años continuos
- **Temporal renovación normal**: misma docs cada año
- **FMM (visitante)**: nuevo cada entrada — no renovación in situ

## Output

```json
{
  "documento_id": "TARJETA-RESIDENTE-TEMPORAL",
  "fecha_emision": "2025-01-15",
  "fecha_vencimiento": "2026-01-14",
  "dias_para_vencer": 217,
  "estado": "vigente",
  "puede_solicitar_permanente": false,
  "anios_continuos": 1,
  "alerta_activa": false
}
```
