---
name: comparador-incoterms
description: Compara costos por INCOTERM (EXW vs FOB vs CIF vs DDP). Quien paga qué. Usar cuando el usuario diga comparador incoterms, comparador_incoterms, ayuda con comparador incoterms.
allowed-tools: Read, Write
---

# Comparador Incoterms

Compara costos por INCOTERM (EXW vs FOB vs CIF vs DDP). Quien paga qué

## Output esperado

```json
{
  "operation": "comparador-incoterms",
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
