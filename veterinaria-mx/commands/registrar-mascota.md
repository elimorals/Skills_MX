---
description: Registra una mascota nueva en el expediente clínico con datos generales, tutor legal, alergias, medicación crónica y vacunas previas.
argument-hint: "[especie, nombre mascota, datos del tutor]"
allowed-tools: Read, Write, Edit
---

# /vet:registrar-mascota

Registra mascota nueva: $ARGUMENTS

## Lo que hace

1. Invoca skill `expediente-clinico-mascota` con datos generales.
2. Captura datos del tutor legal (nombre, WA, email, contacto emergencia).
3. Valida RFC si tutor lo proporciona (skill `rfc-validacion`).
4. Documenta alergias, medicación crónica, cirugías previas.
5. Registra vacunas previas (si tutor las trae) o agenda esquema cachorro si aplica.
6. Genera ID de paciente único: `PET-2026-XXXXXX`.

## Output esperado

```
✓ Mascota registrada — PET-2026-001234

Nombre:    Luna
Especie:   Canino (Labrador, hembra esterilizada)
Edad:      5 años 7 meses
Peso:      28.5 kg
Microchip: 9854321076543210

Tutor:     Ana Martínez (+52555...)
Email:     ana@example.mx
Contacto emergencia: Carlos (+5215587654321)

Alergias documentadas:
  ⚠ Penicilina (anafilaxia 2023)

Medicación crónica:
  • Carprofen 75mg cada 24h (displasia cadera)

Vacunas vigentes:
  ✓ Multivalente DAPP-L (vence 2026-06-15)
  ✓ Antirrábica (vence 2028-06-15)

Próximas:
  ⏰ Multivalente refuerzo: 2026-06-15 (en 4 días)
```
