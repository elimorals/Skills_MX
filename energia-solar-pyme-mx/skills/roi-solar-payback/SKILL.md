---
name: roi-solar-payback
description: Calcula tiempo de recuperación de inversión del sistema solar (típico 3-5 años) con inflación tarifa CFE + degradación paneles. Usar cuando el usuario diga roi solar payback, roi_solar_payback, ayuda con roi solar payback.
allowed-tools: Read, Write
---

# Roi Solar Payback

Calcula tiempo de recuperación de inversión del sistema solar (típico 3-5 años) con inflación tarifa CFE + degradación paneles

## Output esperado

```json
{
  "operation": "roi-solar-payback",
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
