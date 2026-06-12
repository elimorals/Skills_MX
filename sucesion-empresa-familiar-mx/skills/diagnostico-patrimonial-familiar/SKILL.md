---
name: diagnostico-patrimonial-familiar
description: Inventario de bienes (inmuebles, acciones, cuentas, art) + valuación + cálculo patrimonio neto del titular. Usar cuando el usuario diga diagnostico patrimonial familiar, diagnostico_patrimonial_familiar, ayuda con diagnostico patrimonial familiar.
allowed-tools: Read, Write
---

# Diagnostico Patrimonial Familiar

Inventario de bienes (inmuebles, acciones, cuentas, art) + valuación + cálculo patrimonio neto del titular

## Output esperado

```json
{
  "operation": "diagnostico-patrimonial-familiar",
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
