---
name: validador-auditorias-sat-pendientes
description: Detecta si un freelancer / PyME tiene auditorías, requerimientos, o procedimientos del SAT pendientes consultando el Buzón Tributario. Categoriza tipo (revisión electrónica, visita domiciliaria, requerimiento de información, multa, embargo precautorio) y deadline de respuesta. Genera plan de acción priorizando los más urgentes. Usar cuando el usuario diga auditoria SAT, requerimiento SAT, sat me esta investigando, buzón tributario alertas. NO usar para presentar la declaración (es solo lectura).
allowed-tools: Read, Write
---

# Validador auditorías SAT pendientes

## Por qué importa

Una auditoría SAT no respondida en plazo se convierte en presunción de incumplimiento → liquidaciones automáticas que son MUY difíciles de revertir.

## Trigger

- "¿tengo algo pendiente con SAT?"
- "revisa mi buzón"
- Cron mensual / diario (recomendado)

## Flujo

### 1. Consultar Buzón

`mp_sat_portal.sat_descargar_buzon_tributario(rfc)` (mock si sin e.firma, real con e.firma vigente).

### 2. Categorizar notificaciones

| Tipo | Severidad | Deadline típico |
|---|---|---|
| Revisión electrónica | 🟠 Alta | 15 días hábiles |
| Visita domiciliaria | 🔴 Crítica | Inmediato (acudir a domicilio) |
| Requerimiento de información | 🟠 Alta | 10-15 días hábiles |
| Multa firme | 🟡 Media | 30 días para pago |
| Embargo precautorio | 🔴 Crítica | Inmediato |
| Cancelación de CSD | 🔴 Crítica | NO se pueden timbrar CFDIs |
| Carta invitación | 🟡 Media | 60 días para regularizar |

### 3. Output

```json
{
  "rfc_hash": "...",
  "consulta_buzon_fecha": "2026-06-12",
  "total_notificaciones": 4,
  "criticas": 1,
  "altas": 2,
  "medias": 1,
  "items": [
    {
      "tipo": "cancelacion_csd",
      "severidad": "critica",
      "fecha_notificacion": "2026-06-10",
      "fecha_efecto": "2026-06-15",
      "dias_para_actuar": 3,
      "motivo": "Discrepancia ingresos vs depósitos detectada",
      "accion_requerida": "Aclarar discrepancia o re-emitir CSD",
      "alerta_critica": true
    }
  ],
  "vigencia_validada": false
}
```

### 4. Plan de acción

- Cualquier item crítico → 🚨 ACCION HOY
- Cualquier item alto → planificar respuesta esta semana
- Sugerir contador / abogado fiscalista según tipo

## Casos edge

| Caso | Acción |
|---|---|
| Notificación en idioma confuso | Pedir asesoría legal antes de actuar |
| Embargo precautorio | NO operar cuentas sin abogado fiscalista |
| CSD cancelado | Re-tramitar CSD o usar firma alternativa |
| Carta invitación (no obligatoria) | Atender — el SAT te avisa antes de auditoría |

## ⚠ Compliance

- Mock-mode no detecta nada real — pedir e.firma para path real
- `vigencia_validada: false`
- Respuestas mal manejadas tienen consecuencias graves — asesorarse con abogado
