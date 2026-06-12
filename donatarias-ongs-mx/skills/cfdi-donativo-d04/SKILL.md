---
name: cfdi-donativo-d04
description: CFDI uso D04 al donante con datos de donataria autorizada (folio Anexo 14). Donante puede deducir hasta 7% ingreso año anterior. Usar cuando el usuario diga cfdi donativo d04, cfdi_donativo_d04, ayuda con cfdi donativo d04.
allowed-tools: Read, Write
---

# Cfdi Donativo D04

CFDI uso D04 al donante con datos de donataria autorizada (folio Anexo 14). Donante puede deducir hasta 7% ingreso año anterior

## Output esperado

```json
{
  "operation": "cfdi-donativo-d04",
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
