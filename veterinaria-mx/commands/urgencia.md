---
description: Triaje rápido de urgencia veterinaria. Clasifica nivel (1 crítico / 2 urgente / 3 no urgente), da primeros auxilios al tutor por WhatsApp y deriva a clínica o hospital 24h.
argument-hint: "[signos reportados: vómito, sangrado, intoxicación, etc.]"
allowed-tools: Read, Write, Edit
---

# /vet:urgencia

⚠ Triaje urgencia: $ARGUMENTS

## Lo que hace

1. Lee skill `urgencias-protocolo`.
2. Clasifica signos en nivel 1 (crítico), 2 (urgente), 3 (no urgente).
3. Genera mensaje WhatsApp con primeros auxilios apropiados (NO diagnóstico).
4. Si nivel 1: indica venir AHORA + llama al tutor.
5. Si nivel 2: agenda misma tarde/noche.
6. Si nivel 3: agenda regular siguientes días.
7. Si la clínica no atiende nocturno y es nivel 1: deriva a hospital 24h.

## Output esperado (ejemplo nivel 1 crítico)

```
🚨 URGENCIA CRÍTICA — Luna (Labrador 28.5 kg)

Signos reportados:
  • Vómito 5x en 2 horas
  • Abdomen distendido como tambor
  • Letargia extrema

Triaje: NIVEL 1 (CRÍTICO)
Posible: Vólvulo gástrico (torsión)
Tiempo: < 30 minutos para atender

Mensaje enviado a tutor por WhatsApp:
  "Ana, esto es URGENCIA CRÍTICA. NO le des agua.
   Ven AHORA. Si no podemos atenderla en clínica,
   ve a Hospital Veterinario {{hospital}}, dirección {{dir}},
   tel {{tel}}. Estoy llamándote ya."

Acciones automáticas:
  ✓ MVZ Dr. Demo notificado
  ✓ Quirófano preparándose
  ✓ Llamada al tutor en curso
  ✓ Hospital 24h alertado por si requiere derivación

Protocolo activado: VOLVULO_GASTRICO_CANINO_GRANDE
```
