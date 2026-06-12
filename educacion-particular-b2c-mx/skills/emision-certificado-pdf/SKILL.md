---
name: emision-certificado-pdf
description: Certificado profesional firmado digitalmente al completar curso. Útil para LinkedIn / CV.. Usar cuando el usuario diga emision certificado pdf, emision_certificado_pdf, ayuda con emision certificado pdf.
allowed-tools: Read, Write
---

# Emision Certificado Pdf

Certificado profesional firmado digitalmente al completar curso. Útil para LinkedIn / CV.

## Output esperado

```json
{
  "operation": "emision-certificado-pdf",
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
