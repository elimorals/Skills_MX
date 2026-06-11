---
description: Genera copy publicitario para audiencia mexicana en el canal especificado (Meta, Google, TikTok, email, landing).
argument-hint: "<canal> <contexto/producto>"
allowed-tools: Read, Write, Edit
---

# /agencia:copy

Copy para: $ARGUMENTS

1. Invoca el skill `copy-mexicano`.
2. Detecta el canal y formato específico:
   - Meta Ads: primary text + headline + description + 3-5 variantes
   - Google Ads: 15 headlines + 4 descriptions + paths
   - TikTok Ads: hooks de 3 segundos + scripts cortos
   - Email: subject lines + previews + body
   - Landing page: H1 + H2 + CTAs
3. Pide o lee:
   - Producto/servicio a comunicar
   - Audiencia objetivo
   - Tono de marca (si no está documentado, pregúntalo)
   - Cualquier USP, oferta, precio o angle específico
4. Genera 3-5 variantes etiquetadas como "safe" (alta probabilidad) o "experimental" (mayor riesgo, mayor potencial).
5. Aplica validación: sin modismos de España/ARG, sin mayúsculas sostenidas, sin claims sin sustento.
6. Si hay claims que requieren revisión legal (médico, financiero), marca claramente.
7. Guarda en `copy/[cliente]/YYYY-MM-DD-[canal]-[descripcion].md`.
