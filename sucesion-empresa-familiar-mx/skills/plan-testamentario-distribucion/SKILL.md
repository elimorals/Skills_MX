---
name: plan-testamentario-distribucion
description: Distribución óptima de bienes entre herederos según objetivos del titular + legitima 50% irreductible. Usar cuando el usuario diga plan testamentario distribucion, plan_testamentario_distribucion, ayuda con plan testamentario distribucion.
allowed-tools: Read, Write
---

# Plan Testamentario Distribucion

Distribución óptima de bienes entre herederos según objetivos del titular + legitima 50% irreductible

## Output esperado

```json
{
  "operation": "plan-testamentario-distribucion",
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
