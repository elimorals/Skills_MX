---
name: alertas-deadline-anual
description: Calendario de fechas críticas del ciclo de declaración anual ISR para personas físicas en México y alertas asociadas. Cubre fechas SAT fijas (1 febrero–30 abril plazo de la anual PF, 31 marzo anual de PM que afecta a socios, constancias de retenciones e intereses a inicio de año) y permite configurar recordatorios personalizados (cita con contador, fecha objetivo personal, etc.). Genera alertas tipo "faltan X días para Y". Usar cuando el usuario pregunte fechas declaración, cuándo es deadline, calendario fiscal, recordatorios anual. NO usar para deadlines mensuales (eso es del core).
allowed-tools: Read, Write
---

# Alertas y calendario deadline anual

## Calendario fiscal PF — declaración anual

| Fecha | Evento |
|---|---|
| Enero–febrero | Recibir constancias: intereses bancarios, retenciones de plataformas y CFDI de nómina del año (fechas exactas por retenedor: verificar) |
| 31 marzo | Declaración anual de PM (Art. 76 fr. V LISR) — afecta a socios (dividendos) |
| 1 febrero – **30 abril** | **Plazo de la declaración anual PF (Art. 150 LISR)**. Ejercicio 2025 → 30-abr-2026 (jueves); ejercicio 2026 → 30-abr-2027 (viernes) |
| Después del 30 abril | Saldo a pagar genera actualización y recargos (Art. 17-A y 21 CFF); la opción de pagar en hasta 6 parcialidades (Art. 150) exige presentar en plazo |

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
| Mayo en adelante | Seguir devolución (`seguimiento-devolucion-sat`); plazo legal del SAT: 40 días hábiles (Art. 22 CFF) |

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
    {"fecha": "2026-04-30", "evento": "Deadline declaración"}
  ],
  "vigencia_validada": false
}
```

## Casos edge

| Caso | Acción |
|---|---|
| Año bisiesto | 29 febrero existe (consideración manual) |
| Deadline cae en día inhábil | Se recorre al siguiente día hábil (Art. 12 CFF) |
| Usuario fuera del país | Mantener fechas SAT, agregar nota |
| Persona fallecida | Suspender alertas, marcar caso especial |

## Dependencias

- Ninguna externa — calendario hardcoded
- Tracker local de hitos personalizados (archivo JSON en `~/.local/share/plugins-mx/pf-anual/<rfc_hash>/hitos.json`)

## ⚠ Compliance

- Fechas SAT son las publicadas oficialmente (CFF + RMF)
- Si SAT publica calendario distinto (típicamente confirmación en diciembre), actualizar manualmente
