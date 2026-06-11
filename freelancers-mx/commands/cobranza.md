---
description: Calcula y genera el siguiente paso de cobranza para un cliente moroso.
argument-hint: "<cliente> [folio-factura]"
allowed-tools: Read, Write, Edit, Bash
---

# /freelancers:cobranza

Cobranza para: $ARGUMENTS

1. Invoca el skill `cobranza-seguimiento`.
2. Lee la ficha del cliente y el historial de cobranza si existe en `cobranza/[cliente]/historial.md`.
3. Pregunta o detecta:
   - Días de mora actuales
   - Etapa anterior ejecutada (1-5) si la hubo
   - Canal a usar (WhatsApp, email, llamada)
4. Sugiere la etapa apropiada (escalado progresivo).
5. Genera el template del mensaje con datos específicos del cliente y factura.
6. Si es etapa 4+, genera carta formal en `cobranza/[cliente]/carta-DD-MM-AAAA.md`.
7. Registra el evento en `cobranza/[cliente]/historial.md` con timestamp.
8. Recomienda cuándo dar el siguiente paso si este no funciona (típicamente +5 a +10 días).
