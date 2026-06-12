---
name: dashboard-donataria-mes
description: Status mensual de donataria: donativos recibidos por canal, donantes nuevos, projects activos, renovación autorización próxima. Usar cuando el usuario diga dashboard donataria mes, dashboard_donataria_mes, ayuda con dashboard donataria mes.
allowed-tools: Read, Write
---

# Dashboard Donataria Mes

Status mensual de donataria: donativos recibidos por canal, donantes nuevos, projects activos, renovación autorización próxima

## Output esperado

```json
{
  "operation": "dashboard-donataria-mes",
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
