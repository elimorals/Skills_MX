---
name: acreditacion-iva-importacion
description: Acredita IVA pagado en importación en próximo CFDI. Requiere número de pedimento en el CFDI. Usar cuando el usuario diga acreditacion iva importacion, acreditacion_iva_importacion, ayuda con acreditacion iva importacion.
allowed-tools: Read, Write
---

# Acreditacion Iva Importacion

Acredita IVA pagado en importación en próximo CFDI. Requiere número de pedimento en el CFDI

## Output esperado

```json
{
  "operation": "acreditacion-iva-importacion",
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
