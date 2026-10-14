# mp_desconexion_digital

Derecho a la desconexión digital en teletrabajo (LFT Art. 330-E fr. VI + NOM-037-STPS-2023).

**Universo**: empresas con personal en teletrabajo.

## Tools

- `desconexion_checklist(rfc, faltas_marcadas?, modalidad_teletrabajo?)` — ítems obligatorios (con
  base legal) y buenas prácticas (`obligatorio: false`).
- `desconexion_generar_politica(rfc, razon_social, jornada_inicio?, jornada_fin?, canal_denuncia_email?)` — Markdown orientativo.
- `desconexion_template_capacitacion()` — agenda sugerida (no obligatoria por ley).

## Estado real

Tipo: **cálculo normativo local**. Verificado 2026-10-14 contra la LFT vigente
(https://www.diputados.gob.mx/LeyesBiblio/pdf/LFT.pdf, última reforma DOF 14-05-2026) y la
NOM-037-STPS-2023 (DOF 08-06-2023, nota 5691672):

- **No existe** la "reforma LFT Art. 132 de marzo 2026" en la que se basaba este MCP: en el texto
  vigente "desconexión" solo aparece en el Art. 330-E fr. VI (teletrabajo, DOF 11-01-2021).
- Obligatorio en teletrabajo (relaciones > 40 % del tiempo fuera, Art. 330-A): respetar la
  desconexión (330-E fr. VI); contrato con mecanismos de contacto y horarios (330-B fr. VI);
  Política de Teletrabajo con reglas de contacto y derecho a pausas y desconexión (NOM-037 5.2 d, e).
- Sin teletrabajo no hay obligación legal específica; el checklist solo deja buenas prácticas.
- Multas: Art. 1002 LFT (50-5000 UMA) o 994 fr. V (250-5000 UMA) para la NOM; ver `mp_ley_silla_nom037`.
