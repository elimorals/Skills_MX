---
name: compliance-tope-100k-pf
description: Validador del tope de inversión $100k MXN por proyecto para PF normal (mayor si experimentado declarado). Usar cuando el usuario diga compliance tope 100k pf, compliance_tope_100k_pf, ayuda con compliance tope 100k pf.
allowed-tools: Read, Write
---

# Compliance Tope 100K Pf

Validador del tope de inversión $100k MXN por proyecto para PF normal (mayor si experimentado declarado)

## Output esperado

```json
{
  "operation": "compliance-tope-100k-pf",
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
