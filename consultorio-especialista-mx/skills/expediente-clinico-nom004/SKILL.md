---
name: expediente-clinico-nom004
description: Mantiene expediente clínico electrónico conforme NOM-004-SSA3-2012 (criterios obligatorios para elaboración, integración, uso, manejo y confidencialidad). Cubre los 10 elementos: ficha identificación, antecedentes, padecimiento actual, exploración física, diagnósticos, plan tratamiento, pronóstico, notas evolución, recetas/solicitudes, consentimiento informado. Cifrado en reposo. Usar cuando el usuario diga expediente clinico, historia clinica, nom-004, registro paciente.
allowed-tools: Read, Write
---

# Expediente clínico NOM-004

## 10 elementos obligatorios

1. **Ficha identificación**: nombre, edad, sexo, ocupación, domicilio
2. **Antecedentes heredofamiliares**: padre, madre, hermanos, hijos
3. **Antecedentes personales no patológicos**: tabaquismo, alcohol, drogas
4. **Antecedentes personales patológicos**: cirugías, hospitalizaciones, alergias
5. **Padecimiento actual**: cronología + síntomas
6. **Exploración física**: signos vitales + sistemas
7. **Diagnósticos**: CIE-10
8. **Plan tratamiento**: farmacológico + no farmacológico
9. **Pronóstico**: bueno/reservado/malo
10. **Consentimiento informado**: firmado por paciente

## Notas de evolución

Cada consulta de seguimiento agrega:
- Fecha + hora
- Cambios en síntomas
- Modificaciones plan
- Adherencia al tratamiento
- Próxima cita

## ⚠ Compliance

- **Cifrado AES-256 en reposo** (datos sensibles salud)
- Acceso solo médico autorizado
- Auditoría completa (quién leyó qué cuándo)
- Retención mínima: 5 años post última consulta
- Si paciente fallece: conservar 10 años
- Paciente puede solicitar copia (Art. 16 LFPDPPP)

## Output

```json
{
  "expediente_id_hash": "...",
  "paciente_rfc_hash": "...",
  "version_actual": 12,
  "ultima_actualizacion": "2026-06-12T10:30:00",
  "completitud_pct": 95,
  "elementos_faltantes": ["antecedentes_heredofamiliares"],
  "ultima_consulta": "2026-06-12",
  "proxima_sugerida": "2026-09-12",
  "diagnosticos_activos_cie10": ["I10 Hipertensión esencial", "E11.9 Diabetes mellitus tipo 2"]
}
```
