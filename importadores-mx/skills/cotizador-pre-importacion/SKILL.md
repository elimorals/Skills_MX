---
name: cotizador-pre-importacion
description: Calcula costo landing total: IGI + IVA + DTA + prevalidación + flete + seguro. Por fracción arancelaria TIGIE. Usar cuando el usuario diga cotizador pre importacion, cotizador_pre_importacion, ayuda con cotizador pre importacion.
allowed-tools: Read, Write
---

# Cotizador Pre Importacion

Calcula costo landing total: IGI + IVA + DTA + prevalidación + flete + seguro. Por fracción arancelaria TIGIE

## Output esperado

```json
{
  "operation": "cotizador-pre-importacion",
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
