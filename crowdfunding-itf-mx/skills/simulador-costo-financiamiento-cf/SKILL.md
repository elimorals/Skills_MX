---
name: simulador-costo-financiamiento-cf
description: Para emprendedor: compara costo total financiamiento via CF (deuda/equity) vs banco tradicional. Usar cuando el usuario diga simulador costo financiamiento cf, simulador_costo_financiamiento_cf, ayuda con simulador costo financiamiento cf.
allowed-tools: Read, Write
---

# Simulador Costo Financiamiento Cf

Para emprendedor: compara costo total financiamiento via CF (deuda/equity) vs banco tradicional

## Output esperado

```json
{
  "operation": "simulador-costo-financiamiento-cf",
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
