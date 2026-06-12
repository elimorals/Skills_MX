---
name: workflow-procesar-wa-pendientes
description: Procesa en batch los mensajes WhatsApp pendientes de respuesta en el inbox (alimentado por webhook Meta WA). Clasifica cada mensaje por intent (consulta cotización, pago confirmado, queja, agendar cita, otro), genera respuesta sugerida con plantilla apropiada, y deja en cola para confirmación del operador antes de enviar. Útil al inicio del día o después de fin de semana. Usar cuando el usuario diga procesa mis WhatsApp, qué WA tengo pendientes, contesta los WhatsApp, procesar inbox. NO usar para envío masivo (eso es `cobranza-multinivel`).
allowed-tools: Read, Write, Bash
---

# Workflow: Procesar WhatsApp pendientes

Triage de bandeja de entrada WhatsApp para que el operador no tenga que leer cada mensaje desde cero.

## Cuándo correr

- Inicio del día (8-9am)
- Tras fin de semana / vacaciones (acumulación)
- Después de campaña masiva (respuestas entrantes)

## Inputs

- `inbox`: `~/.local/share/plugins-mx/wa-inbox.jsonl` (alimentado por handler webhook `meta_whatsapp` en `webhooks/app/handlers/`)
- `limite`: N mensajes a procesar por sesión (default 50)
- `solo_pendientes`: bool — saltar ya procesados

## Fases

### Fase 1 — Cargar inbox pendientes

```bash
jq -r 'select(.status == "pending")' ~/.local/share/plugins-mx/wa-inbox.jsonl | head -50
```

### Fase 2 — Clasificación por intent

Por cada mensaje, identificar intent:

| Intent | Palabras clave detectables |
|---|---|
| `pago_confirmado` | "ya pague", "ya deposite", "transferí", "te mando comprobante", "spei", "pagado" |
| `cotizacion_pedida` | "cuánto cuesta", "tienes precio", "cotización", "presupuesto" |
| `agendar_cita` | "cita", "agendar", "horario", "disponibilidad", "domingo", "lunes..." |
| `queja_o_inconformidad` | "no me gustó", "queja", "molesto", "denunciar", "condusef", "profeco" |
| `solicitar_factura` | "factura", "cfdi", "ya me la pueden facturar", "rfc para factura" |
| `confirmar_servicio` | "ok", "perfecto", "va", "trato hecho", "acepto" |
| `solicitar_info` | "qué tal", "cómo funciona", "información", "duda" |
| `cancelar` | "ya no", "cancelo", "no gracias" |
| `otro` | (no clasificable) |

### Fase 3 — Generar respuesta sugerida

Por intent, usar plantilla:

```
pago_confirmado → "Gracias por avisar. Verifico depósito y te confirmo factura."
cotizacion_pedida → "Con gusto te paso cotización. ¿Qué servicio necesitas?"
agendar_cita → "Claro, mi disponibilidad: <lunes-viernes 10-18>. ¿Qué horario te queda?"
queja → ⚠ NO autogenerar. Operador debe leer personalmente.
solicitar_factura → "Mándame tu RFC + razón social + uso CFDI para emitir."
```

### Fase 4 — Cola de confirmación

Cada respuesta sugerida va a `~/.local/share/plugins-mx/wa-outbox-borrador.jsonl` con flag `requiere_aprobacion: true`.

Operador revisa y aprueba uno por uno (o invoca `/core:wa-aprobar-todos` para batch).

### Fase 5 — Output

```json
{
  "workflow": "procesar_wa_pendientes",
  "fecha": "2026-06-12",
  "mensajes_procesados": 32,
  "por_intent": {
    "pago_confirmado": 8,
    "cotizacion_pedida": 5,
    "agendar_cita": 4,
    "queja_o_inconformidad": 1,
    "solicitar_factura": 3,
    "confirmar_servicio": 7,
    "otro": 4
  },
  "respuestas_sugeridas": 30,
  "requieren_atencion_humana": 2,
  "alertas": [
    "1 queja detectada — leer personalmente"
  ],
  "siguiente_paso": "Revisar cola en wa-outbox-borrador.jsonl"
}
```

## Casos edge

| Caso | Acción |
|---|---|
| Mensaje en lenguaje no español | No procesar, marcar `requiere_humano` |
| Mensaje con imagen/audio/video | No clasificar texto, marcar |
| Mensaje muy largo (> 500 chars) | Resumir antes de mostrar sugerencia |
| Conversación multi-mensaje | Agrupar por número + ventana temporal |
| Número no registrado en clientes | Sugerir agregar al CRM antes de responder |

## Dependencias

- Webhook handler `meta_whatsapp` (alimenta inbox)
- `mp_meta_whatsapp.send_message` (envío tras aprobación)
- Tracker de clientes para matching de número

## ⚠ Compliance

- Hashear números teléfono en logs
- Quejas NUNCA autoresponderse
- Política Meta: respuesta dentro de ventana 24h conversación abierta; fuera, requiere plantilla aprobada
