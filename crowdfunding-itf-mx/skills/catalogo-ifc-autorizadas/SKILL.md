---
name: catalogo-ifc-autorizadas
description: Listado oficial CNBV de las 70+ IFC autorizadas con sus condiciones (tasas, plazos, tipos crowdfunding). Usar cuando el usuario diga catalogo ifc autorizadas, catalogo_ifc_autorizadas, ayuda con catalogo ifc autorizadas.
allowed-tools: Read, Write
---

# Catalogo Ifc Autorizadas

Listado oficial CNBV de las 70+ IFC autorizadas con sus condiciones (tasas, plazos, tipos crowdfunding)

## Output esperado

```json
{
  "operation": "catalogo-ifc-autorizadas",
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
