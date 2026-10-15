---
name: validador-auditorias-sat-pendientes
description: Detecta si un freelancer / PyME tiene auditorías, requerimientos, o procedimientos del SAT pendientes consultando el Buzón Tributario. Categoriza tipo (revisión electrónica, visita domiciliaria, requerimiento de información, multa, embargo precautorio) y deadline de respuesta. Genera plan de acción priorizando los más urgentes. Usar cuando el usuario diga auditoría SAT, requerimiento SAT, el SAT me está investigando, carta invitación, me restringieron el sello, buzón tributario alertas. NO usar para presentar la declaración (es solo lectura).
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

`mp_sat_portal.sat_descargar_buzon_tributario` **no está implementado**: con credenciales devuelve `UpstreamError` con `handoff_url`; sin credenciales, datos mock. Entrega al usuario la URL, pídele entrar con e.firma o contraseña y copiar/descargar las notificaciones; categoriza lo que comparta. Nunca presentes datos mock como reales.

### 2. Categorizar notificaciones

| Tipo | Severidad | Deadline típico |
|---|---|---|
| Revisión electrónica (Art. 53-B CFF) | 🟠 Alta | 15 días hábiles para desvirtuar la resolución provisional |
| Visita domiciliaria (Art. 46 CFF) | 🔴 Crítica | Inmediato; plazos por acta |
| Requerimiento de información (Art. 53 CFF) | 🟠 Alta | 6 o 15 días hábiles según el tipo; leer el oficio |
| Crédito fiscal / multa | 🟡 Media | 30 días hábiles para pagar o impugnar (Arts. 65 y 121 CFF) |
| Embargo precautorio | 🔴 Crítica | Inmediato |
| Restricción temporal de CSD (Art. 17-H Bis CFF) | 🔴 Crítica | No puedes facturar; solicitar aclaración (hasta 40 días hábiles) para restablecerlo |
| Carta invitación | 🟡 Media | Sin plazo legal; atenderla pronto evita una revisión |

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
      "tipo": "restriccion_temporal_csd",
      "severidad": "critica",
      "fecha_notificacion": "2026-06-10",
      "fecha_efecto": "2026-06-10",
      "plazo_aclaracion_dias_habiles": 40,
      "motivo": "Discrepancia ingresos vs depósitos detectada",
      "accion_requerida": "Presentar caso de aclaración (Art. 17-H Bis) con pruebas para restablecer el CSD",
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
| CSD restringido | Aclaración vía caso en el portal SAT; mientras tanto no se puede timbrar |
| Carta invitación (no obligatoria) | Atender — el SAT te avisa antes de auditoría |

## ⚠ Compliance

- El MCP no lee el Buzón real (no implementado): la fuente es lo que el usuario copie del portal
- `vigencia_validada: false`
- Respuestas mal manejadas tienen consecuencias graves — asesorarse con abogado
