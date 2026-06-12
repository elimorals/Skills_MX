---
name: fiscal-rendimientos-p2p
description: Cálculo ISR sobre intereses recibidos en P2P + retención plataforma + acreditación en anual. Usar cuando el usuario diga fiscal rendimientos p2p, fiscal_rendimientos_p2p, ayuda con fiscal rendimientos p2p.
allowed-tools: Read, Write
---

# Fiscal Rendimientos P2P

Cálculo ISR sobre intereses recibidos en P2P + retención plataforma + acreditación en anual

## Output esperado

```json
{
  "operation": "fiscal-rendimientos-p2p",
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
