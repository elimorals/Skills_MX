---
name: simulador-donacion-vs-herencia
description: Compara 4 escenarios (testar todo, donar parte, trust, sociedad familiar) con impacto fiscal cada uno. Usar cuando el usuario diga simulador donacion vs herencia, simulador_donacion_vs_herencia, ayuda con simulador donacion vs herencia.
allowed-tools: Read, Write
---

# Simulador Donacion Vs Herencia

Compara 4 escenarios (testar todo, donar parte, trust, sociedad familiar) con impacto fiscal cada uno

## Output esperado

```json
{
  "operation": "simulador-donacion-vs-herencia",
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
