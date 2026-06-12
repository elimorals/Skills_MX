---
name: optimizacion-tarifa-gdmth
description: Sugerencias para mover consumo a horarios base (madrugada) vs punta (1pm-4pm) para reducir costo en tarifa GDMTH. Usar cuando el usuario diga optimizacion tarifa gdmth, optimizacion_tarifa_gdmth, ayuda con optimizacion tarifa gdmth.
allowed-tools: Read, Write
---

# Optimizacion Tarifa Gdmth

Sugerencias para mover consumo a horarios base (madrugada) vs punta (1pm-4pm) para reducir costo en tarifa GDMTH

## Output esperado

```json
{
  "operation": "optimizacion-tarifa-gdmth",
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
