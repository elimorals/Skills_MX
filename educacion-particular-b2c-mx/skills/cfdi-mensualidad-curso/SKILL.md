---
name: cfdi-mensualidad-curso
description: CFDI G03 si educación particular o D10 con Complemento IEDU si academia RVOE. Pago no efectivo obligatorio para deducir. Usar cuando el usuario diga cfdi mensualidad curso, cfdi_mensualidad_curso, ayuda con cfdi mensualidad curso.
allowed-tools: Read, Write
---

# Cfdi Mensualidad Curso

CFDI G03 si educación particular o D10 con Complemento IEDU si academia RVOE. Pago no efectivo obligatorio para deducir

## Output esperado

```json
{
  "operation": "cfdi-mensualidad-curso",
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
