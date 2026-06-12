---
name: declaracion-anual-transparencia
description: Generador de declaración informativa anual (31 mayo) con patrimonio + destino donativos + actividades realizadas. Usar cuando el usuario diga declaracion anual transparencia, declaracion_anual_transparencia, ayuda con declaracion anual transparencia.
allowed-tools: Read, Write
---

# Declaracion Anual Transparencia

Generador de declaración informativa anual (31 mayo) con patrimonio + destino donativos + actividades realizadas

## Output esperado

```json
{
  "operation": "declaracion-anual-transparencia",
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
