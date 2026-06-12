---
name: calculo-isr-donaciones
description: Cónyuges + ascendientes/descendientes directos: EXENTO sin tope. Otros familiares: gravable Art. 96 con exención $600k anual. Usar cuando el usuario diga calculo isr donaciones, calculo_isr_donaciones, ayuda con calculo isr donaciones.
allowed-tools: Read, Write
---

# Calculo Isr Donaciones

Cónyuges + ascendientes/descendientes directos: EXENTO sin tope. Otros familiares: gravable Art. 96 con exención $600k anual

## Output esperado

```json
{
  "operation": "calculo-isr-donaciones",
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
