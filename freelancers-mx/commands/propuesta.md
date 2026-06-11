---
description: Genera propuesta comercial completa (3-15 páginas) para un cliente.
argument-hint: "<cliente> [proyecto/oportunidad]"
allowed-tools: Read, Write, Edit, Bash
---

# /freelancers:propuesta

Genera propuesta para: $ARGUMENTS

1. Invoca el skill `propuesta-comercial`.
2. Recopila contexto:
   - Quien es el cliente (industria, tamaño, contactos)
   - Cómo surgió la oportunidad
   - Qué problema enfrenta
   - Stakeholders involucrados
   - Presupuesto declarado o estimado
   - Plazo y restricciones
3. Estructura la propuesta con resumen ejecutivo, entendimiento, solución, equipo, casos, económicos, términos.
4. Aplica `iva-retenciones-mx` a los económicos.
5. Genera en markdown y guárdala en `propuestas/YYYY-MM-DD-[cliente]-[proyecto].md`.
6. Sugiere versión PDF para envío (skill `pdf`).
7. Sugiere mensaje teaser breve para enviar antes de la propuesta completa.
