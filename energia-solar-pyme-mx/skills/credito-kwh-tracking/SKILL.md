---
name: credito-kwh-tracking
description: Tracking del crédito kWh acumulado mes a mes. CFE no paga efectivo - solo crédito. Usar cuando el usuario diga credito kwh tracking, credito_kwh_tracking, ayuda con credito kwh tracking.
allowed-tools: Read, Write
---

# Credito Kwh Tracking

Tracking del crédito kWh acumulado mes a mes. CFE no paga efectivo - solo crédito

## Output esperado

```json
{
  "operation": "credito-kwh-tracking",
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
