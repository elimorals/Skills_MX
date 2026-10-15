---
name: generador-constancias-curp
description: Ayuda a obtener la constancia de CURP (Clave Única de Registro de Población) del portal gob.mx/curp de RENAPO - valida localmente la estructura de la CURP, intenta la consulta y, como el portal tiene CAPTCHA y anti-bot, entrega al usuario la URL y los pasos para descargar el PDF con QR él mismo. Útil para trámites donde piden la CURP impresa. Usar cuando el usuario diga descargar CURP, constancia CURP, imprimir CURP, consultar mi CURP, no sé mi CURP.
allowed-tools: Read, Write
---

# Constancia de CURP

## Estado real del MCP

`mp_curp_renapo` está en **"entrega a humano"**: gob.mx/curp usa Akamai y reCAPTCHA Enterprise; hoy el anti-bot bloquea antes del captcha. `curp_consultar_renapo`, `curp_consultar_renapo_por_datos` y `curp_descargar_constancia_renapo` devuelven `requiere_humano: true` con URL y pasos (en modo `PLUGINS_MX_MOCK=1` devuelven datos simulados: nunca los presentes como reales).

## Flujo

1. Si el usuario da la CURP: valida con `curp_validar_estructura` (local) y deriva fecha, sexo y entidad (`curp_derivar_fecha_nacimiento`, `curp_derivar_sexo`, `curp_derivar_estado`).
2. Si no la sabe: pide nombre(s), apellidos, fecha y entidad de nacimiento, sexo. `curp_generar_desde_datos` da una CURP **probable**, sin la homoclave oficial: no la presentes como definitiva.
3. Llama `curp_descargar_constancia_renapo`. Si responde `requiere_humano`, entrega al usuario la URL y los pasos que devuelve el tool (entrar a gob.mx/curp, capturar CURP o datos, resolver el captcha, descargar PDF).
4. Si el usuario sube el PDF descargado, guárdalo en `~/.local/share/plugins-mx/curp/<hash>.pdf` (sin la CURP en el nombre del archivo).

## Output

```json
{
  "curp": "PEGJ900101HDFRRN01",
  "estructura_valida": true,
  "consulta_renapo": "requiere_humano",
  "url_portal": "https://www.gob.mx/curp/",
  "pasos_usuario": ["Abrir la URL", "Capturar CURP", "Resolver captcha", "Descargar PDF"],
  "constancia_pdf_path": null,
  "fecha": "2026-10-15"
}
```

## Casos edge

- Datos en RENAPO con errores (nombre, fecha): la corrección se hace en el Registro Civil / RENAPO, no en el portal.
- CURP biométrica (con fotografía): reforma a la Ley General de Población (DOF 16-07-2025); su obligatoriedad y calendario: **verificar** antes de afirmarlo al usuario.

## Dependencia

`mp_curp_renapo` (validación local real; consulta RENAPO = entrega a humano).
Datos personales: trata la CURP conforme al skill `compliance-lfpdppp`.
