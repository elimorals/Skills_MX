---
name: agendar-consulta-remota
description: Agenda consulta remota con paciente y genera link de videollamada (Zoom / Google Meet / Teams). Pre-requisitos digitales (consentimiento firmado, pago si aplica). Envía link al paciente 30 min antes via email y WhatsApp con instrucciones técnicas. Usar cuando el usuario diga agendar consulta online, programar videollamada paciente, agendar telemedicina.
allowed-tools: Read, Write
---

# Agendar consulta remota

## Schema cita remota

```python
class ConsultaRemota(BaseModel):
    consulta_id: str
    paciente_id_hash: str
    fecha_hora: datetime
    duracion_min: int
    plataforma: Literal["zoom", "google_meet", "teams", "doxy"]
    link_videocall: str
    paciente_consentimiento_firmado: bool
    paciente_pago_recibido: bool  # típico pre-pago
    paciente_pre_requisitos_completos: bool
    motivo_consulta: str
    requiere_estudios_previos: bool
    timezone_paciente: str  # crítico — paciente puede estar fuera de MX
```

## Pre-requisitos antes de confirmar

```python
def validar_pre_requisitos(cita: ConsultaRemota) -> dict:
    bloqueos = []
    if not cita.paciente_consentimiento_firmado:
        bloqueos.append("Falta consentimiento informado firmado")
    if not cita.paciente_pago_recibido and EXIGE_PREPAGO:
        bloqueos.append("Falta pago confirmado")
    return {"puede_confirmar": len(bloqueos) == 0, "bloqueos": bloqueos}
```

## Flujo

1. Paciente solicita cita (vía formulario / WhatsApp)
2. Sistema verifica consentimiento previo (si nuevo: solicitar firma)
3. Sistema solicita pago (procesador Stripe/MP/Conekta)
4. Si todo OK: generar link videocall
5. Confirmación al paciente vía email + WA
6. Recordatorios: 24h, 30min, 5min antes
7. Post-consulta: link a expediente + receta si aplica

## Output

```json
{
  "consulta_id": "TEL-001",
  "fecha_hora": "2026-06-15T16:00:00-06:00",
  "paciente_timezone": "America/Mexico_City",
  "plataforma": "zoom",
  "link_videocall": "https://zoom.us/j/...",
  "duracion_min": 30,
  "pre_requisitos_completos": true,
  "recordatorios_programados": ["24h", "30min", "5min"],
  "estado": "confirmada"
}
```

## Casos edge

- Paciente fuera de MX (otra timezone): mostrar siempre hora local del paciente
- Conexión lenta: ofrecer audio-only fallback
- Paciente menor de edad: padre/tutor debe estar presente
- Plataforma cae: tener backup (ej. WhatsApp video)
