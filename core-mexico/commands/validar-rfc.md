---
description: Valida estructuralmente uno o más RFCs mexicanos (PF/PM) y reporta resultados.
argument-hint: "<rfc1> [rfc2 rfc3...]"
allowed-tools: Read, Bash
---

# /core:validar-rfc

Valida los RFCs proporcionados: $ARGUMENTS

1. Invoca el skill `rfc-validacion` con cada RFC argumentado.
2. Para cada RFC reporta:
   - RFC normalizado (mayúsculas, sin guiones)
   - Tipo: PF (13 chars) o PM (12 chars)
   - Validación estructural: ✓ o ✗
   - Si ✗, razones específicas
   - Si es genérico (XAXX/XEXX), señalar restricciones de uso
   - Alertas (palabras inconvenientes, fechas dudosas, etc.)
3. Si la integración SAT está configurada y el usuario lo solicita, consultar estatus en padrón y lista 69-B (EFOS).
4. Devolver tabla resumen.
