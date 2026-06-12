---
name: alertas-deadline-anual
description: Calendario de fechas críticas del ciclo de declaración anual ISR para personas físicas en México y alertas asociadas. Cubre fechas SAT fijas (30 abril deadline general, 15 enero plazo retenciones del año anterior por parte de patrones, 31 marzo plazo para declaraciones de PM que afectan a PF socias) y permite configurar recordatorios personalizados (cita con contador, fecha objetivo personal, etc.). Genera alertas tipo "faltan X días para Y". Usar cuando el usuario pregunte fechas declaración, cuándo es deadline, calendario fiscal, recordatorios anual. NO usar para deadlines mensuales (eso es del core).
allowed-tools: Read, Write
---

# Alertas y calendario deadline anual

## Calendario fiscal PF — declaración anual

| Fecha | Evento |
|---|---|
| 15 enero | Plazo para que patrones emitan CFDI nómina con resumen anual del ejercicio anterior |
| 31 enero | Plazo para retenciones a cuenta del año anterior por terceros (clientes que retuvieron) |
| 31 marzo | Plazo declaraciones anuales PM (afecta a PF socias / accionistas) |
| **30 abril** | **Deadline declaración anual PF (Cap. II y deducciones personales)** |
| 30 junio | Plazo para presentar complementarias sin recargo |
| Después | Complementarias con recargos progresivos |

## Hitos sugeridos para el contribuyente

| Fecha | Acción sugerida |
|---|---|
| 1 enero | Reinicia conteo de gastos médicos, hospitales, etc. del año en curso |
| 31 enero | Verifica recepción de constancia de retenciones (clientes / banco) |
| Marzo (primer fin de semana) | Recopila CFDIs (invocar `recopilar-cfdis-anuales`) |
| 1 abril | Calcula primer borrador (invocar `calculadora-isr-anual`) |
| 15 abril | Revisar con contador certificado |
| 25 abril | Presentar en DeclaraSAT (margen) |
| 30 abril | Deadline |
| 1 mayo - 30 junio | Seguir devolución (`seguimiento-devolucion-sat`) |

## Alertas a generar

### En sesión actual

Si hoy ∈ ventana crítica:

```
📅 Faltan {N} día(s) para el deadline del 30 abril {año}

✅ Hecho:
  - Borrador calculado (saldo a pagar $X)
  - Validación con contador: pendiente

⚠ Pendiente:
  - Revisar 5 CFDIs con UUID cancelado
  - Confirmar deducciones personales (2 médicos en efectivo, NO aplican)

Sugerencias:
  1. Agendar contador esta semana
  2. Generar PDF final con `generar-borrador-declaracion`
```

### En sesión futura

Permite scheduling vía `cron` o trackeo de fecha objetivo:

```json
{
  "tipo": "recordatorio",
  "fecha_alerta": "2026-04-15",
  "evento": "Cita con contador para revisión declaración",
  "rfc_hash": "...",
  "ejercicio": 2025
}
```

## Output al invocar

```json
{
  "hoy": "2026-04-10",
  "ejercicio_en_curso": 2025,
  "dias_para_deadline_principal": 20,
  "estado_borrador": "calculado",
  "validacion_contador": "pendiente",
  "alertas_activas": [
    {"prioridad": "alta", "mensaje": "Faltan 20 días para deadline 30 abril 2026"},
    {"prioridad": "media", "mensaje": "Borrador calculado pero sin revisión de contador"}
  ],
  "proximos_hitos": [
    {"fecha": "2026-04-15", "evento": "Cita contador (configurado)"},
    {"fecha": "2026-04-30", "evento": "Deadline declaración"},
    {"fecha": "2026-06-30", "evento": "Plazo complementaria sin recargo"}
  ],
  "vigencia_validada": true
}
```

## Casos edge

| Caso | Acción |
|---|---|
| Año bisiesto | 29 febrero existe (consideración manual) |
| Deadline cae en fin de semana | SAT permite hasta lunes siguiente |
| Usuario fuera del país | Mantener fechas SAT, agregar nota |
| Persona fallecida | Suspender alertas, marcar caso especial |

## Dependencias

- Ninguna externa — calendario hardcoded
- Tracker local de hitos personalizados (archivo JSON en `~/.local/share/plugins-mx/pf-anual/<rfc_hash>/hitos.json`)

## ⚠ Compliance

- Fechas SAT son las publicadas oficialmente (CFF + RMF)
- Si SAT publica calendario distinto (típicamente confirmación en diciembre), actualizar manualmente
