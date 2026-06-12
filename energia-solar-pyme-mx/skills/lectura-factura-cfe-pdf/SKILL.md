---
name: lectura-factura-cfe-pdf
description: Parser PDF factura CFE bidireccional. Extrae consumo + inyección + crédito kWh acumulado + cargo demanda + factor potencia. Usar cuando el usuario diga lectura factura cfe pdf, lectura_factura_cfe_pdf, ayuda con lectura factura cfe pdf.
allowed-tools: Read, Write
---

# Lectura Factura Cfe Pdf

Parser PDF factura CFE bidireccional. Extrae consumo + inyección + crédito kWh acumulado + cargo demanda + factor potencia

## Output esperado

```json
{
  "operation": "lectura-factura-cfe-pdf",
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
