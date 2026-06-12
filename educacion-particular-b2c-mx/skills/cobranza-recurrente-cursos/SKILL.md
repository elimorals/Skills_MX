---
name: cobranza-recurrente-cursos
description: Cobranza recurrente mensual con escalado empático (alumnos = relación continua). Usar cuando el usuario diga cobranza recurrente cursos, cobranza_recurrente_cursos, ayuda con cobranza recurrente cursos.
allowed-tools: Read, Write
---

# Cobranza Recurrente Cursos

Cobranza recurrente mensual con escalado empático (alumnos = relación continua)

## Output esperado

```json
{
  "operation": "cobranza-recurrente-cursos",
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
