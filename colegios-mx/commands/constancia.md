---
description: Genera constancia académica (inscripción, estudios, boleta) para un alumno con datos SEP correctos.
argument-hint: "<alumno> [tipo: inscripcion|estudios|boleta]"
allowed-tools: Read, Write, Edit
---

# /colegios:constancia

Constancia para: $ARGUMENTS

1. Invoca `constancias-academicas`.
2. Detecta tipo de constancia solicitada.
3. Lee datos del alumno desde el sistema interno o pide capturarlos.
4. Lee config del colegio en `config/colegio.json` (razón social, CCT, RVOE, director).
5. Valida CURP estructuralmente.
6. Genera documento en markdown estructurado con membretado simulado.
7. Si es boleta: pide calificaciones por materia y valida rango (5.0-10.0 en básica).
8. Marca puntos pendientes de firma autógrafa y sello.
9. Sugiere conversión a PDF para impresión en papel membretado.
10. Registra emisión en `constancias/historico-emisiones.md`.
