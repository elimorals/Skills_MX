---
name: pedimento-tracker
description: Tracking de pedimentos pendientes con clave (A1/F4/V1) + agente aduanal + estado aduana. Usar cuando el usuario diga pedimento tracker, pedimento_tracker, ayuda con pedimento tracker.
allowed-tools: Read, Write
---

# Pedimento Tracker

Tracking de pedimentos pendientes con clave (A1/F4/V1) + agente aduanal + estado aduana

## Output esperado

```json
{
  "operation": "pedimento-tracker",
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
