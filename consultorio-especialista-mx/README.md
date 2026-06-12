# consultorio-especialista-mx

Plugin para médicos especialistas con consultorio privado en México (80k profesionales).

> Score research: **8.3/10**. Patrón clonado de `veterinaria-mx` + compliance NOM-004.

## Diferencias

| Vertical | Diferencia |
|---|---|
| `veterinaria-mx` | Pacientes animales |
| `telemedicina-mx` | Consultas remotas |
| `consultorio-especialista-mx` | Especialista presencial (cardio, derma, ped, etc.) |
| `clinica-salud-mx` | Multiconsultorio con varios médicos |

## Skills

1. `agenda-pacientes-consultorio` — citas físicas
2. `expediente-clinico-nom004` — cumplimiento NOM-004 SSA3
3. `receta-electronica-cofepris` — receta con e.firma médico (bloquea Grupo I-II)
4. `cobranza-consultas-especialista` — incluye seguros / GMM
5. `dashboard-consultorio-mes` — ingresos + paciente top

## ⚠ Compliance

- Cédula profesional + cédula especialidad vigentes
- LFPDPPP + LGPDPPSO con datos sensibles
- CFDI uso D01 (honorarios médicos)
- COFEPRIS si maneja medicamentos controlados
