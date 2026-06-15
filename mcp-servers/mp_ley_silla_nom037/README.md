# mp_ley_silla_nom037

Compliance Ley Silla + NOM-035 + NOM-037 + Desconexión Digital (Reforma LFT Art. 132 marzo 2026).

**Universo**: 4M empresas formales mexicanas con trabajadores.

**Por qué urge**: fase vigilancia STPS arranca 2026 con multas $29k–$586k MXN + suspensión.

## Tools

- `silla_verificar_compliance(rfc, num_empleados, giro, modalidad_remota?, faltas_marcadas?)` — checklist + score + multa potencial.
- `silla_calcular_multa(severidad, reincidente?)` — rango MXN para una falta.
- `silla_generar_politica(rfc, razon_social, giro, modalidad, nombre_responsable_sst)` — política Markdown firmable consolidada (Silla + NOM-035 + Desconexión).
- `silla_listar_obligaciones(marco)` — catálogo público por marco (`ley_silla`/`nom035`/`nom037`/`desconexion_digital`).

## Base legal

- LFT reforma DOF 17-jul-2025 (Ley Silla)
- NOM-035-STPS-2018 (psicosociales)
- NOM-037-STPS-2023 (teletrabajo)
- LFT Art. 132 reforma marzo 2026 (desconexión digital)
