---
name: protocolo-familiar-template
description: Template editable de protocolo familiar para empresa familiar: reglas de gobierno, sucesión gerencia, accionistas familiares. Usar cuando el usuario diga protocolo familiar template, protocolo_familiar_template, ayuda con protocolo familiar template.
allowed-tools: Read, Write
---

# Protocolo Familiar Template

Template editable de protocolo familiar para empresa familiar: reglas de gobierno, sucesión gerencia, accionistas familiares

## Output esperado

```json
{
  "operation": "protocolo-familiar-template",
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
