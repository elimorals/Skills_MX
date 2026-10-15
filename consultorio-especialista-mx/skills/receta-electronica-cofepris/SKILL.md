---
name: receta-electronica-cofepris
description: Generación de receta electrónica para consultorio médico especialista presencial. Incluye datos del médico (nombre, cédula profesional y de especialidad si aplica, domicilio), paciente, diagnóstico CIE-10, medicamentos en denominación genérica con dosis, vía, intervalo y duración, firma electrónica y QR. Clasifica cada medicamento por las reglas de venta de la LGS (Art. 226, listas de los Arts. 234 y 245): estupefacientes van en recetario especial con código de barras y psicotrópicos en receta que la farmacia retiene. Usar cuando el usuario diga emitir receta, prescribir, receta electrónica, receta cofepris, receta de controlados, receta de benzodiacepinas.
allowed-tools: Read, Write
---

# Receta electrónica — consultorio

> Apoyo al médico; la prescripción y la firma son su responsabilidad. No existe (revisado 2026-10-15) un esquema federal de receta electrónica para controlados; no prometer aceptación en farmacia.

## Datos de la receta

- **Médico**: nombre, cédula profesional, cédula de especialidad si aplica, domicilio del consultorio, firma (autógrafa o electrónica)
- **Paciente**: nombre completo, edad, sexo; peso recomendado en pediatría
- **Diagnóstico** (CIE-10), registrado también en la nota de evolución (NOM-004-SSA3-2012 6.2)
- **Medicamentos**: **denominación genérica obligatoria** (marca opcional, LGS Art. 226 último párrafo), presentación, dosis, vía, intervalo, duración
- **Indicaciones no farmacológicas** y fecha de emisión

Requisitos de forma del Reglamento de Insumos para la Salud: **verificar** (no cotejados en esta revisión).

## Reglas de venta (LGS vigente, últimas reformas DOF 15-01-2026)

| Categoría | Ejemplos | Regla | Vía electrónica |
|---|---|---|---|
| Estupefacientes (Art. 234) → Art. 226 fr. I | morfina, fentanilo, oxicodona, metadona, buprenorfina, metilfenidato | Recetario especial con código de barras asignado por la SSA (trámite COFEPRIS-03-006); tratamiento ≤ 30 días; prescriben médicos cirujanos, no se exige especialidad (Arts. 240-241) | ❌ Bloquear |
| Psicotrópicos Art. 245 fr. III → Art. 226 fr. II | alprazolam, clonazepam, diazepam, lorazepam, tramadol | Receta con cédula; se surte una vez y se retiene; vigencia 30 días (Art. 251) | ⚠ Avisar: aceptación electrónica **verificar** |
| Psicotrópicos Art. 245 fr. IV → Art. 226 fr. III | fenobarbital | Hasta 3 surtidos en 6 meses (Art. 252) | ⚠ Avisar |
| Art. 226 fr. IV | mayoría de medicamentos con receta | Resurtible según indique el médico | ✅ |

"Grupos I-VI" no es terminología de la ley: usar fracciones del Art. 226. La fracción de cada producto consta en su registro sanitario.
MCP: `mp_expediente_clinico_nom024` → `ece_generar_receta` (clasifica y calcula vigencia, cálculo local) y `mp_sep_profesional` → `sep_validar_medico_para_consulta` (si devuelve `requiere_humano: true`, dar al usuario la URL y pasos para confirmar la cédula).

## Algoritmo de bloqueo

```python
def emitir_receta(medicamentos: list[Medicamento]) -> dict:
    clasif = [clasificar(m) for m in medicamentos]      # LGS Arts. 226, 234, 245
    if any(c.categoria == "estupefaciente_art234" for c in clasif):
        return {
            "error": "RECETARIO_ESPECIAL_REQUERIDO",
            "razon": "Estupefaciente: recetario especial con código de barras (LGS Arts. 240-241)",
            "receta_emitida": None,
        }
    avisos = [f"{c.nombre}: la farmacia retiene la receta ({c.regla})"
              for c in clasif if c.categoria.startswith("psicotropico")]
    # ... generar, firmar y registrar QR
```

## Output

```json
{
  "receta_id": "REC-MOCK-001",
  "fecha_emision": "2026-10-15T11:00:00-06:00",
  "medico_cedula": "1234567",
  "paciente_curp_hash": "abc12345",
  "diagnostico_cie10": "I10",
  "medicamentos": [
    {"generico": "Losartán", "presentacion": "50 mg tab", "dosis": "1 cada 24 h", "via": "oral",
     "duracion_dias": 30, "fraccion_art226": "IV"}
  ],
  "avisos_psicotropicos": [],
  "qr_verificacion": "https://verificar.consultorio.mx/REC-001",
  "firma_medico_aplicada": true,
  "pdf_path": "~/.local/share/plugins-mx/recetas/REC-MOCK-001.pdf"
}
```
