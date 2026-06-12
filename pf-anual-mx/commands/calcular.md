---
description: Calcula ISR anual + compara con pagos provisionales (genera saldo a pagar / a favor).
---

Invoca `calculadora-isr-anual` con los inputs del dataset construido por `recopilar-cfdis-anuales` + `identificar-deducciones-personales`.

Argumentos:
- `ejercicio`
- `regimen` ∈ {PFAE_612, RESICO_PF_626, ASALARIADO_HONORARIOS_605}

Output:
- ISR causado
- Saldo (a pagar / a favor)
- Recomendaciones
- ⚠ `vigencia_validada: false` — validar con contador antes de presentar
