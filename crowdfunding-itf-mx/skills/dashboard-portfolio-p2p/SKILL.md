---
name: dashboard-portfolio-p2p
description: Status portafolio P2P: capital prestado, rendimientos pendientes, en mora, diversificación por plataforma + industria. Usar cuando el usuario diga dashboard portfolio p2p, dashboard_portfolio_p2p, ayuda con dashboard portfolio p2p.
allowed-tools: Read, Write
---

# Dashboard Portfolio P2P

Status portafolio P2P: capital prestado, rendimientos pendientes, en mora, diversificación por plataforma + industria

## Output esperado

```json
{
  "operation": "dashboard-portfolio-p2p",
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
