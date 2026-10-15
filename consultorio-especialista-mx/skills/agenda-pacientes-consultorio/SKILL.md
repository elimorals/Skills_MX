---
name: agenda-pacientes-consultorio
description: Gestión de agenda de pacientes para consultorio médico especialista en México (presencial). Cubre citas programadas, recordatorios automáticos WhatsApp 24h y 2h antes, manejo de cancelaciones, lista de espera para huecos, integración con calendar (Google/iCal), y prevención de overbooking. Considera horario laborable real del consultorio (a diferencia de telemedicina, que puede ser 24/7). Usar cuando el usuario diga agenda consultorio, citas pacientes, programar cita, calendario de consultas, reagendar paciente, lista de espera.
allowed-tools: Read, Write
---

# Agenda consultorio especialista

## Datos esenciales por cita

```python
class CitaConsultorio(BaseModel):
    cita_id: str
    paciente_id: str
    paciente_nombre: str
    paciente_tel: str
    fecha_hora: datetime
    duracion_min: int  # típico 30-60
    tipo: Literal["primera_vez", "seguimiento", "urgencia", "videoconsulta"]
    motivo_consulta_breve: str
    estado: Literal["programada", "confirmada", "en_curso", "completada", "cancelada", "no_asistio"]
    cobro_estimado_mxn: Decimal
    requiere_estudios_previos: bool
```

## Recordatorios automáticos

- **24h antes**: WhatsApp con confirmación (Sí/No/Reagendar)
- **2h antes**: WhatsApp recordatorio con dirección + parking
- **Post-consulta**: WhatsApp con receta + plan de seguimiento

## Lista de espera

Si paciente quiere cita pronto pero no hay espacio:
- Agregar a lista por orden de llegada
- Si cancela alguien: ofrecer hueco a primero en lista (5 min para confirmar)

## Output dashboard

```
📅 Agenda hoy — 2026-06-12

09:00 — Juan P.   primera vez — cardiología
10:00 — María L.  seguimiento — eco previo OK
10:30 — Carlos R. urgencia — IAM sospecha
11:30 — LIBRE
12:00 — Ana V.    seguimiento

📞 Lista de espera (3):
  • Pedro M. — primera vez — espera hueco esta semana
  • Sofía T. — seguimiento — espera hueco próxima
```

## Casos edge

- Paciente no llega: dejar 15 min, después marcar no_asistio + cobrar penalización solo si la política se informó por escrito al agendar (LFPC)
- Urgencia mid-day: reagendar cita programada
- Cancelación última hora: enviar a lista de espera
- Recordatorios por WhatsApp: plantillas aprobadas por Meta, opt-in del paciente y sin motivo de consulta ni diagnóstico en el texto (dato sensible, LFPDPPP 2025) → skill compartida `whatsapp-business-mx`
