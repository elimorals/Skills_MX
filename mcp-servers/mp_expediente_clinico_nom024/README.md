# mp_expediente_clinico_nom024

Expediente Clínico Electrónico (ECE) + Receta electrónica NOM-024-SSA3-2012.

**DOF 15-ene-2026**: digitalización obligatoria del sector salud.

**Universo**: ~70k médicos privados + ~20k clínicas + ~5k hospitales privados MX.

## Tools

- `ece_generar_receta(medico_cedula, medico_nombre, especialidad, paciente_*, medicamentos[], diagnostico)` — receta firmable con clasificación COFEPRIS.
- `ece_verificar_medico(cedula)` — delega a `mp_sep_profesional` (mock).
- `ece_validar_sistema(sistema_id, capacidades[])` — checklist NOM-024.
- `ece_consentimiento_paciente(curp, proposito)` — token consentimiento informado.

## Vertical desbloqueado

`telemedicina-mx` ya scaffoldeado pasa de stub a funcional.
