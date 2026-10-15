---
name: emision-certificado-pdf
description: Genera la constancia o certificado PDF de terminación de un curso particular, con folio único, datos del alumno y del curso, horas, fecha, firma del instructor o director y código QR o URL de verificación. Distingue constancia sin validez oficial (cursos sin RVOE), constancia DC-3 de competencias laborales (solo agentes capacitadores registrados ante la STPS) y documentos con RVOE. Útil para LinkedIn o CV. Usar cuando el usuario diga emisión certificado PDF, constancia de curso, diploma curso, certificado de terminación, DC-3, certificado para LinkedIn.
allowed-tools: Read, Write
---

# Emisión de constancia o certificado de curso

## Elige el tipo correcto

| Tipo | Cuándo | Qué decir en el documento |
|---|---|---|
| Constancia de participación o terminación | Curso sin RVOE (la mayoría) | "Constancia de terminación del curso … Documento sin validez oficial ante la SEP." |
| DC-3 (constancia de competencias o habilidades laborales) | Capacitación a trabajadores de una empresa, impartida por agente capacitador externo registrado ante la STPS | Formato DC-3 de la STPS con su número de registro de agente capacitador |
| Certificado con validez oficial | Solo planes con RVOE | Lo emite la institución conforme a su RVOE y la autoridad educativa; no lo genera esta skill |

Nunca escribas "certificado oficial", "avalado por la SEP" ni "con validez oficial" si el curso no tiene RVOE: ostentar validez oficial sin tenerla puede ser publicidad engañosa (LFPC).

## Contenido

- Nombre de la academia (razón social) y logo
- Nombre completo del alumno
- Nombre del curso, horas totales, modalidad y fechas de inicio y fin
- Calificación o "aprobado", si aplica
- Folio único (p. ej. `ACAD-2026-000123`) y fecha de emisión
- Firma del instructor o director: imagen de firma autógrafa o firma electrónica. La e.firma del SAT no es necesaria para una constancia privada.
- QR o URL de verificación que consulte el folio en el registro de la academia
- Leyenda de validez según la tabla

## Flujo

1. Confirma en el tracker que el alumno terminó y que el curso está pagado.
2. Genera el PDF con folio consecutivo y guarda el hash SHA-256 del archivo en el registro de emisiones.
3. Envía el PDF y el enlace de verificación por email o WhatsApp.

## Output esperado

```json
{
  "operation": "emision-certificado-pdf",
  "data": {
    "folio": "ACAD-2026-000123",
    "tipo": "constancia_sin_validez_oficial",
    "alumno": "Ana López Ruiz",
    "curso": "Python básico",
    "horas": 40,
    "fecha_emision": "2026-10-14",
    "sha256": "…",
    "url_verificacion": "https://…/verificar/ACAD-2026-000123"
  },
  "vigencia_validada": true
}
```
