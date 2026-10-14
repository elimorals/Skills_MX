# mp_expediente_clinico_nom024

Expediente clínico electrónico (SIRES, NOM-024-SSA3-2012) + receta con reglas de venta de la LGS.

**Universo**: ~70k médicos privados + ~20k clínicas + ~5k hospitales privados MX.

## Tools

- `ece_generar_receta(...)` — borrador firmable; por medicamento anota categoría (LGS Art. 234 /
  245), fracción de venta (Art. 226), vigencia y surtidos; avisa si exige recetario especial.
- `ece_verificar_medico(cedula)` — valida formato; la vigencia se consulta con `mp_sep_profesional`
  (`vigente: null`).
- `ece_validar_sistema(sistema_id, capacidades[])` — autoevaluación por numeral de la NOM-024.
- `ece_consentimiento_paciente(curp, proposito)` — plantilla.

## Estado real

Tipo: **cálculo normativo local**. Verificado 2026-10-14 (detalle en `shared/ece_nom024_mx.py`):

| Tema | Valor | Fuente |
|---|---|---|
| SIRES | 6.5.1 CURP validada; 6.6.1 SGSI (CIA + trazabilidad + no repudio); 6.6.2 documentos inalterables y FEA; 6.6.3 autenticación; 6.6.4 roles; 6.6.6 exportación/consentimientos; HL7 opcional (6.1.3.1) | NOM-024-SSA3-2012, DOF 30-11-2012 (nota 5280847) |
| Conservación | ≥ 5 años desde el último acto médico | NOM-004-SSA3-2012 5.4, DOF 15-10-2012 (nota 5272787) |
| Estupefacientes (morfina, fentanilo, oxicodona, metadona, buprenorfina, metilfenidato) | Art. 226 fr. I; recetario especial con código de barras, tratamiento ≤ 30 días | LGS Arts. 234, 240-242 |
| Psicotrópicos fr. III (alprazolam, clonazepam, diazepam, lorazepam, tramadol) | Art. 226 fr. II: receta con cédula, se surte una vez y se retiene; vigencia 30 días | LGS Arts. 226, 245, 251 |
| Psicotrópicos fr. IV (fenobarbital) | Art. 226 fr. III: hasta 3 surtidos en 6 meses | LGS Arts. 245, 252 |
| Denominación genérica | Obligatoria | LGS Art. 226 (DOF 30-03-2022) |
| Decreto DOF 15-01-2026 | Agrega "Salud Digital" (Arts. 71 Bis-71 Octies): obliga a instituciones públicas y fija condiciones a la telesalud | LGS vigente |

Corregido: el decreto del 15-01-2026 **no** vuelve obligatorio el ECE para privados; morfina no
tiene "vigencia 1 día" ni exige cédula de especialidad (prescriben médicos cirujanos, Art. 240);
las benzodiacepinas no son "fracción IV" y metilfenidato está en la lista de estupefacientes;
`ece_verificar_medico` decidía la vigencia con el último dígito de la cédula.

No cotejado: requisitos de forma de la receta del Reglamento de Insumos para la Salud.
