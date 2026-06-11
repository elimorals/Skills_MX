---
description: Genera certificado de garantía al cierre de OT o gestiona reclamo de garantía vigente.
argument-hint: "<accion: certificado|reclamo> <OT-folio>"
allowed-tools: Read, Write, Edit, Bash
---

# /talleres:garantia

Garantía: $ARGUMENTS

1. Invoca `garantia-servicio`.
2. Si acción = "certificado":
   - Lee OT cerrada.
   - Genera certificado completo con trabajos cubiertos, plazos (30d MO, 90d refacción), qué cubre / qué no.
   - Guarda en `garantias/[OT].md`.
   - Sugiere imprimir + entregar al cliente al recoger el auto.
3. Si acción = "reclamo":
   - Lee OT original y certificado.
   - Valida vigencia (días desde cierre vs plazos).
   - Conduce flujo de validación del reclamo (Caso A cubierta / B falla nueva / C uso indebido / D más diagnóstico).
   - Genera comunicación al cliente apropiada.
   - Si Caso B/C, genera nueva cotización con `diagnostico-cotizacion`.
   - Documenta en `garantias/[OT]/reclamo-[fecha].md` para respaldo PROFECO si aplica.
