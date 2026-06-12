---
name: agenda-multi-medico
description: Agenda compartida de clínica con N médicos cada uno con su horario de atención, especialidad, y consultorios físicos. Permite recepción/secretaría asignar paciente al médico apropiado, ver disponibilidad cruzada, y manejar suplencias. Usar cuando el usuario diga agenda clinica multimedico, asignar paciente, ver disponibilidad medicos.
allowed-tools: Read, Write
---

# Agenda multi-médico clínica

## Schema

```python
class MedicoClinica(BaseModel):
    medico_id: str
    cedula_profesional: str
    nombre: str
    especialidades: list[str]
    consultorio_asignado: str | None  # algunos rotan
    dias_semana: list[Literal["L","M","X","J","V","S"]]
    horario_inicio: time
    horario_fin: time
    comision_pct: float  # típico 60-70%
    activo: bool
```

## Lógica asignación

```python
def asignar_cita(motivo: str, urgencia: str, preferencia_medico: str | None) -> Asignacion:
    # 1. Si paciente prefiere médico específico, asignar si tiene espacio
    # 2. Si no, buscar médico con especialidad apropiada al motivo
    # 3. Asignar al médico con menor carga del día
    # 4. Verificar consultorio físico disponible (si la clínica tiene N consultorios)
    pass
```

## Output

```
🏥 AGENDA HOY — Clínica La Salud

09:00-13:00:
  Dr. Ramírez (Cardio) — Consult. 1 — 4 citas (1 hueco 11:30)
  Dra. López (Pediatría) — Consult. 2 — 6 citas (lleno)
  Dr. Suárez (Med Gen) — Consult. 3 — 5 citas (2 huecos)

14:00-18:00:
  Dra. Martínez (Derma) — Consult. 1 — 3 citas (3 huecos)
  Dr. Ramírez (Cardio) — fuera (clínica privada)

Recepción: 32 huecos disponibles esta semana
```
