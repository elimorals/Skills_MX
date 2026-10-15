---
name: recordatorios-paciente-wa
description: Recordatorios automáticos por WhatsApp Business a pacientes de telemedicina con plantillas aprobadas por Meta - 24h antes (confirmación), 2h antes (link + tips técnicos), post-consulta (resumen + receta + próxima cita sugerida) y recordatorios de medicamento (crónicos con opt-in). Ayuda a bajar el no-show; mide tu tasa antes y después. Sin diagnósticos en los mensajes (datos sensibles). Usar cuando el usuario diga recordatorios paciente, whatsapp paciente, no-show telemedicina, confirmar cita por WhatsApp, recordatorio de medicamento.
allowed-tools: Read, Write
---

# Recordatorios WhatsApp pacientes

## Calendario de recordatorios

### T-24h: Confirmación
```
Hola [Nombre]! 👋

Te recordamos tu consulta de mañana:
📅 [Fecha] a las [Hora]
📍 Modalidad: Videollamada (link te llegará 30 min antes)

¿Sigue en pie? Responde:
✅ SÍ — quedan confirmados
❌ NO — reagendamos
```

### T-2h: Link + tips
```
Hola [Nombre], faltan 2 horas para tu consulta.

🔗 Link: https://zoom.us/j/...
📱 También por celular si es más fácil

Tips para mejor consulta:
• Conecta a WiFi 5-10 min antes para verificar
• Cierra otras apps con cámara
• Lugar tranquilo + iluminado

¡Te veo en 2 horas!
```

### Post-consulta (mismo día)
```
Hola [Nombre], gracias por la consulta de hoy.

Resumen:
• Plan: [tratamiento breve]
• Receta: [link PDF firmado]
• Próxima consulta sugerida: [fecha]

Cualquier duda escríbeme. Mucho ánimo. 💚
```

### Recordatorios medicamentos (si paciente crónico opt-in)
```
Recordatorio medicamento:
💊 [Nombre medicamento] [Dosis]
Tómalo ahora con un vaso de agua.

¿Lo tomaste? [SÍ/NO]
```

## Output

```json
{
  "paciente_id_hash": "...",
  "consulta_id": "TEL-001",
  "recordatorios_programados": [
    {"tipo": "24h_confirmacion", "ts": "2026-06-14T16:00", "estado": "enviado"},
    {"tipo": "2h_link_tips", "ts": "2026-06-15T14:00", "estado": "pendiente"},
    {"tipo": "post_consulta_resumen", "ts": "2026-06-15T17:00", "estado": "pendiente"}
  ],
  "opt_in_medicamentos_diarios": false,
  "tasa_no_show_actual": 6.5
}
```

## Compliance WA

- Plantillas aprobadas por Meta (categoría UTILITY); detalle en la skill compartida `whatsapp-business-mx`
- Costo: desde el 01-07-2025 Meta cobra por mensaje de plantilla entregado; presupuestar 3-4 plantillas por consulta
- Opt-in registrado (paciente lo aceptó en el consentimiento) y opt-out en cualquier momento
- Sin diagnóstico, medicamento psiquiátrico ni motivo de consulta en texto libre: son datos sensibles (LFPDPPP 2025 Art. 8); el resumen clínico va en link autenticado, no en el chat
- Hash del número en logs

Métrica: compara la tasa de no-show 4 semanas antes y después de activar recordatorios; no hay una cifra de reducción garantizada.
