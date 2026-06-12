---
name: catalogo-tigie-busqueda
description: Búsqueda de fracción arancelaria 8 dígitos por nombre producto. Top 200 fracciones comunes precargadas. Usar cuando el usuario diga catalogo tigie busqueda, catalogo_tigie_busqueda, ayuda con catalogo tigie busqueda.
allowed-tools: Read, Write
---

# Catalogo Tigie Busqueda

Búsqueda de fracción arancelaria 8 dígitos por nombre producto. Top 200 fracciones comunes precargadas

## Output esperado

```json
{
  "operation": "catalogo-tigie-busqueda",
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
