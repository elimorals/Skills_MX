---
name: dashboard-academia-online
description: Dashboard ingresos del mes + alumnos activos por curso + tasa completacion + churn. Usar cuando el usuario diga dashboard academia online, dashboard_academia_online, ayuda con dashboard academia online.
allowed-tools: Read, Write
---

# Dashboard Academia Online

Dashboard ingresos del mes + alumnos activos por curso + tasa completacion + churn

## Output esperado

```json
{
  "operation": "dashboard-academia-online",
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
