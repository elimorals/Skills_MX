---
name: generador-constancias-curp
description: Generación/descarga de constancia de CURP (Clave Única de Registro de Población) desde el portal RENAPO. Útil cuando se requiere para trámites donde la persona no tiene la constancia física a la mano. La constancia digital es válida con QR oficial. Usar cuando el usuario diga descargar curp, constancia curp, imprimir curp.
allowed-tools: Read, Write
---

# Generador constancia CURP

## Trigger

- Trámites donde se pide CURP impresa (escuela, banco, trabajo)
- Renovación documentos
- Cuando no se sabe la CURP exacta

## Flujo

1. Pedir al usuario: nombre completo, fecha nacimiento, lugar de nacimiento, sexo
2. Consultar RENAPO (vía `mp_curp_renapo`)
3. Descargar PDF oficial de constancia con QR
4. Guardar en `~/.local/share/plugins-mx/curp/<rfc_o_hash>.pdf`

## Output

```json
{
  "curp": "PEGJ900101HDFRRN01",
  "nombre_completo": "...",
  "fecha_nacimiento": "1990-01-01",
  "constancia_pdf_path": "...",
  "qr_verificacion_url": "https://www.gob.mx/curp/...",
  "vigente": true,
  "fecha_descarga": "2026-06-12"
}
```

## Dependencia

`mp_curp_renapo` (ya existe en repo).
