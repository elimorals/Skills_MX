---
name: inscripcion-alumno-curso
description: Onboarding alumno con datos básicos + asignación curso + pago primer mes. Usar cuando el usuario diga inscripcion alumno curso, inscripcion_alumno_curso, ayuda con inscripcion alumno curso.
allowed-tools: Read, Write
---

# Inscripcion Alumno Curso

Onboarding alumno con datos básicos + asignación curso + pago primer mes

## Output esperado

```json
{
  "operation": "inscripcion-alumno-curso",
  "data": {},
  "vigencia_validada": false
}
```

## Casos edge

- Datos incompletos → solicitar al usuario
- Modo mock por default si no hay credenciales

## Dependencias

- `core-mexico` (CFDI, RFC, mxn-formato)
- Tracker local
