---
name: expediente-clinico-nom004
description: Mantiene el expediente clínico (en papel o electrónico) conforme NOM-004-SSA3-2012 - historia clínica (interrogatorio, exploración física, estudios, diagnósticos, pronóstico, indicación terapéutica), notas de evolución, cartas de consentimiento informado cuando aplican, firma y conservación mínima de 5 años. Si es electrónico, requisitos de NOM-024-SSA3-2012 (CURP, bitácora, roles, firma electrónica avanzada). Usar cuando el usuario diga expediente clínico, historia clínica, nom-004, nota de evolución, registro del paciente, cuánto tiempo guardo expedientes.
allowed-tools: Read, Write
---

# Expediente clínico NOM-004-SSA3-2012

> Apoyo documental; el contenido clínico es responsabilidad del médico.

## Historia clínica (6.1), en este orden

1. **Interrogatorio (6.1.1)**: ficha de identificación, grupo étnico en su caso, antecedentes heredo-familiares, personales patológicos (incluye tabaco, alcohol y otras sustancias) y no patológicos, padecimiento actual (incluye tratamientos previos convencionales, alternativos y tradicionales), interrogatorio por aparatos y sistemas
2. **Exploración física (6.1.2)**: habitus exterior, signos vitales (temperatura, TA, FC, FR), peso y talla, cabeza, cuello, tórax, abdomen, miembros y genitales (o lo que corresponda a la especialidad)
3. **Resultados de estudios (6.1.3)**: laboratorio, gabinete y otros
4. **Diagnósticos o problemas clínicos (6.1.4)** — CIE-10 recomendado
5. **Pronóstico (6.1.5)**
6. **Indicación terapéutica (6.1.6)**

## Nota de evolución (6.2) — en cada consulta

Evolución y actualización del cuadro, signos vitales según se considere necesario, resultados relevantes, diagnósticos, pronóstico, tratamiento e indicaciones (medicamentos con dosis, vía y periodicidad). Las recetas y solicitudes deben ser congruentes con esta nota.

## Reglas generales

- Toda nota: fecha, hora, nombre completo y firma autógrafa, electrónica o digital (5.10); lenguaje técnico, sin abreviaturas ni enmendaduras (5.11)
- Medios electrónicos permitidos de forma optativa (5.12)
- **Cartas de consentimiento informado** (10.1): obligatorias en los eventos de 10.1.2 — ingreso hospitalario, cirugía mayor, anestesia general o regional, salpingoclasia/vasectomía, trasplantes, investigación, necropsia, procedimientos de alto riesgo, mutilación. Para consulta externa ordinaria son opcionales (10.1.3), pero el consentimiento para tratar datos de salud sí es obligatorio (LFPDPPP 2025 Art. 8)

## ⚠ Conservación y acceso

- El expediente es propiedad del prestador; el paciente tiene derechos de titularidad sobre su información (5.4)
- **Conservación: mínimo 5 años desde el último acto médico** (5.4). La NOM no fija un plazo distinto por fallecimiento
- Confidencialidad: no divulgar datos que identifiquen al paciente sin autorización escrita (5.5, 5.7)
- El paciente solicita **por escrito** el resumen clínico u otras constancias (5.6); como titular de datos también tiene derechos ARCO: respuesta en 20 días hábiles y 15 para hacerlo efectivo (Art. 31 LFPDPPP 2025)
- Autoridades judiciales, de procuración de justicia y administrativas pueden requerir el expediente (5.6)

## Si es electrónico (NOM-024-SSA3-2012)

CURP como identificador (6.5.1); seguridad con confidencialidad, integridad, disponibilidad, trazabilidad y no repudio (6.6.1); documentos inalterables y firma electrónica avanzada (6.6.2); autenticación y roles (6.6.3-6.6.4); exportación y control de consentimientos (6.6.6). Cifrado en reposo y bitácora de accesos son la forma práctica de cumplirlo.
El decreto LGS DOF 15-01-2026 (Salud Digital) no vuelve obligatorio el expediente electrónico para consultorios privados.

MCP opcional: `mp_expediente_clinico_nom024` → `ece_validar_sistema` (autoevaluación local por numeral, no certificación).

## Output

```json
{
  "expediente_id_hash": "...",
  "paciente_curp_hash": "...",
  "version_actual": 12,
  "ultima_actualizacion": "2026-10-15T10:30:00-06:00",
  "completitud_pct": 95,
  "elementos_faltantes": ["antecedentes_heredo_familiares"],
  "ultima_consulta": "2026-10-15",
  "conservar_hasta_minimo": "2031-10-15",
  "proxima_sugerida": "2027-01-15",
  "diagnosticos_activos_cie10": ["I10 Hipertensión esencial", "E11.9 Diabetes mellitus tipo 2"]
}
```
