---
name: renovacion-autorizacion-anual
description: Tracking de fecha renovación + alertas 90 días antes + documentos requeridos. Usar cuando el usuario diga renovacion autorizacion anual, renovacion_autorizacion_anual, ayuda con renovacion autorizacion anual.
allowed-tools: Read, Write
---

# Renovacion Autorizacion Anual

Tracking de fecha renovación + alertas 90 días antes + documentos requeridos

## Output esperado

```json
{
  "operation": "renovacion-autorizacion-anual",
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
