---
name: agenda-citas-personal
description: Agenda personal de citas médicas del paciente con N especialistas. Coordina horarios, recordatorios, notas pre-cita (síntomas a mencionar), seguimiento post-cita. Útil para pacientes con múltiples condiciones que ven varios médicos. Usar cuando el usuario diga mis citas medicas, agenda paciente, proxima consulta.
allowed-tools: Read, Write
---

# Agenda personal del paciente

## Schema

```python
class CitaPersonal(BaseModel):
    fecha_hora: datetime
    medico_nombre: str
    especialidad: str
    consultorio_direccion: str
    motivo_consulta: str
    sintomas_a_mencionar: list[str]
    examenes_traer: list[str]
    medicamentos_actuales: list[str]
    notas_post_cita: str
    proxima_sugerida: date
```

## Output

```
🩺 MIS CITAS

Próximas:
  • 2026-06-18 10:00 — Dr. Ramírez (Cardiólogo)
    Motivo: control HTA
    Llevar: ECG último, lista medicamentos actuales

  • 2026-06-25 16:00 — Dra. López (Endocrinóloga)
    Motivo: control DM2
    Llevar: glucemia capilar últimas 2 semanas, HbA1c

📋 Pendientes:
  • Agendar oftalmólogo (anual, requiere fundo de ojo)
```
