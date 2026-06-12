---
description: Distribución de propinas del día siguiendo modelo configurado (100% mesero / tip pool / híbrido / por horas).
argument-hint: "[fecha y turno, ej. 'sábado noche']"
allowed-tools: Read, Write, Edit
---

# /restaurante:distribuir-propinas

Distribuye propinas: $ARGUMENTS

## Lo que hace

Skill `propinas-distribucion` calcula reparto según modelo configurado:
1. **100% mesero**: cada mesero su propina íntegra (Art. 346 LFT puro)
2. **Tip pool**: 70% meseros + 20% cocina + 10% bar
3. **Híbrido**: mesero conserva 70-80%, aporta el resto al pool
4. **Por horas**: tickets por puesto × valor

Genera bitácora trazable con firma digital del trabajador.

⚠ Cumple Art. 346 LFT: propinas son del trabajador, no del restaurante.
