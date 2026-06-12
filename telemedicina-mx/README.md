# telemedicina-mx

Plugin para médicos / psicólogos / profesionales de salud con consultas remotas en México.

> Spec: `docs/specs/07-vertical-telemedicina-mx.md`
> Score research: **8.5/10**. Mercado: ~35k profesionales post-COVID.

## Diferencias

| Vertical | Cobertura |
|---|---|
| `consultorio-especialista-mx` | Médico especialista PRESENCIAL |
| `clinica-salud-mx` | Multiconsultorio físico |
| `psicoterapia-mx` | Psicólogo terapia (presencial o remoto) |
| **`telemedicina-mx`** | Consulta REMOTA por video (medicina, psicología, otros) |

## Skills (10)

1. `dashboard-consultas-telemedicina`
2. `agendar-consulta-remota` (con link Zoom/Meet)
3. `expediente-clinico-tele` (NOM-004 cifrado)
4. `receta-electronica-tele-cofepris` (bloquea Grupo I-II)
5. `consentimiento-informado-tele`
6. `cfdi-honorario-medico-d01`
7. `cobranza-terapia-recurrente-tele`
8. `recordatorios-paciente-wa`
9. `interacciones-medicamentosas-basicas`
10. `compliance-lgpdppso-salud`

## Comandos (5)

```
/tele:dashboard
/tele:agendar
/tele:receta
/tele:expediente
/tele:facturar
```

## Workflow

`workflow-consulta-remota-completa` — end-to-end de consulta.

## ⚠ Compliance

- **NOM-024-SSA3-2010**: receta electrónica con e.firma
- **NOM-004-SSA3-2012**: expediente clínico obligatorio
- **Reforma LGS 2026**: telemedicina reconocida explícitamente
- **Medicamentos controlados Grupos I-II**: bloqueados (requieren receta física)
- **LGPDPPSO**: datos sensibles de salud cifrados AES-256

Ver spec completo: `docs/specs/07-vertical-telemedicina-mx.md`.
