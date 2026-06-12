---
name: validacion-factura-cfe
description: Detecta errores comunes facturación CFE (DAP duplicado, factor potencia mal cobrado, tarifa cambiada sin aviso). Usar cuando el usuario diga validacion factura cfe, validacion_factura_cfe, ayuda con validacion factura cfe.
allowed-tools: Read, Write
---

# Validacion Factura Cfe

Detecta errores comunes facturación CFE (DAP duplicado, factor potencia mal cobrado, tarifa cambiada sin aviso)

## Output esperado

```json
{
  "operation": "validacion-factura-cfe",
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
