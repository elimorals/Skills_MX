---
name: reporte-mensual-efectivo-100k
description: Reporte LFPRH si > $100k MXN efectivo en mes. Obligatorio - omitir tiene sanción severa. Usar cuando el usuario diga reporte mensual efectivo 100k, reporte_mensual_efectivo_100k, ayuda con reporte mensual efectivo 100k.
allowed-tools: Read, Write
---

# Reporte Mensual Efectivo 100K

Reporte LFPRH si > $100k MXN efectivo en mes. Obligatorio - omitir tiene sanción severa

## Output esperado

```json
{
  "operation": "reporte-mensual-efectivo-100k",
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
