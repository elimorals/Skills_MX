---
name: receta-electronica-tele-cofepris
description: Arma la receta electrónica de una consulta remota con datos del médico (cédula), paciente, diagnóstico, medicamentos en denominación genérica con dosis, vía, intervalo y duración, firma electrónica y QR de verificación. Clasifica cada medicamento por las reglas de venta de la LGS (Art. 226 y listas de los Arts. 234 y 245) y bloquea la vía electrónica para estupefacientes (recetario especial con código de barras) y avisa en psicotrópicos (receta que la farmacia retiene). Usar cuando el usuario diga receta tele, receta electrónica, prescripción remota, prescribir online, receta por videoconsulta, medicamento controlado en telemedicina.
allowed-tools: Read, Write
---

# Receta electrónica — telemedicina

> Herramienta de apoyo. La decisión de prescribir y la firma son del médico. No hay en la LGS ni en un decreto localizado (revisado 2026-10-15) un esquema federal de "receta electrónica COFEPRIS" para medicamentos controlados; no prometer que la farmacia la aceptará.

## Validaciones antes de emitir

1. **Cédula profesional** del médico: `mp_sep_profesional` → `sep_validar_medico_para_consulta`. El portal de la SEP exige CAPTCHA: si el tool devuelve `requiere_humano: true`, entregar al usuario la URL y pasos que regresa y pedir que confirme él.
2. **Firma electrónica** del médico vigente (NOM-024-SSA3-2012 6.6.2 pide que el sistema permita la firma electrónica avanzada).
3. **Paciente identificado** (nombre; CURP si el sistema es SIRES, NOM-024 6.5.1).
4. **Diagnóstico** registrado en la nota de evolución (NOM-004 6.2).
5. **Denominación genérica obligatoria**; la marca es opcional (LGS Art. 226, último párrafo, DOF 30-03-2022).
6. **Clasificación de venta** de cada medicamento (tabla siguiente).

## Reglas de venta (LGS vigente, últimas reformas DOF 15-01-2026)

| Categoría | Ejemplos | Regla | ¿Receta electrónica? |
|---|---|---|---|
| Estupefacientes (Art. 234) → Art. 226 fr. I | morfina, fentanilo, oxicodona, metadona, buprenorfina, metilfenidato | Recetario especial con código de barras asignado por la SSA; tratamientos ≤ 30 días (Arts. 240-241) | ❌ **Bloquear**: usar recetario especial físico |
| Psicotrópicos Art. 245 fr. III → Art. 226 fr. II | alprazolam, clonazepam, diazepam, lorazepam, tramadol | Receta con número de cédula; se surte una vez y la farmacia la retiene; vigencia 30 días; máx. 2 presentaciones (Arts. 226 fr. II, 251) | ⚠ Avisar: la farmacia debe retener la receta; aceptación de receta electrónica **verificar** con la farmacia/autoridad estatal |
| Psicotrópicos Art. 245 fr. IV → Art. 226 fr. III | fenobarbital | Hasta 3 surtidos en 6 meses; se retiene en el tercero (Art. 252) | ⚠ Igual que arriba |
| Art. 226 fr. IV (resurtible) | antihipertensivos, antibióticos y la mayoría de medicamentos con receta | Se resurte las veces que indique el médico | ✅ |
| Art. 226 fr. V-VI | venta sin receta | — | ✅ (opcional) |

La fracción exacta de cada producto está en su registro sanitario; si no está en el catálogo, marcar "verificar".
MCP: `mp_expediente_clinico_nom024` → `ece_generar_receta` anota categoría, fracción, vigencia y surtidos por medicamento (cálculo local; los requisitos de forma del Reglamento de Insumos para la Salud no están cotejados).

## Algoritmo

```python
def emitir_receta_tele(medico, paciente, diagnostico, medicamentos) -> dict:
    cedula = sep_validar_medico_para_consulta(medico.cedula)
    if cedula.get("requiere_humano"):
        return {"estado": "requiere_humano", "pasos": cedula.get("handoff")}  # URL + pasos para el usuario
    if not cedula.get("vigente"):
        return {"error": "CEDULA_NO_VIGENTE"}
    if not medico.firma_electronica_vigente():
        return {"error": "FIRMA_ELECTRONICA_NO_VIGENTE"}

    clasif = [clasificar(m) for m in medicamentos]          # Art. 226 / 234 / 245
    if any(c.categoria == "estupefaciente_art234" for c in clasif):
        return {"error": "RECETARIO_ESPECIAL_REQUERIDO",
                "razon": "Estupefaciente: recetario especial con código de barras (LGS Arts. 240-241)"}

    receta = generar_pdf(medico, paciente, diagnostico, medicamentos)  # genérico obligatorio
    return {
        "receta_id": receta.id,
        "pdf_firmado": firmar(receta, medico.firma),
        "qr_url": registrar_qr(receta.id),
        "contiene_psicotropico": any(c.categoria.startswith("psicotropico") for c in clasif),
        "vigencia_dias": min((c.vigencia_receta_dias for c in clasif if c.vigencia_receta_dias), default=None),
    }
```

`vigencia_dias = None` significa que la ley no fija vigencia (fr. IV); no inventar "90 días estándar".

## QR de verificación

Permite a la farmacia confirmar autenticidad, integridad y si ya se surtió. Es un mecanismo del sistema del médico, no un registro oficial de COFEPRIS.

## Output

```json
{
  "receta_id": "REC-TEL-001",
  "fecha_emision": "2026-10-15T16:30:00-06:00",
  "modalidad": "telemedicina",
  "medico_cedula": "1234567",
  "cedula_vigente": true,
  "paciente_curp_hash": "...",
  "diagnostico_cie10": "I10",
  "medicamentos": [
    {"generico": "Losartán", "presentacion": "50 mg tab", "dosis": "1 cada 24 h", "via": "oral",
     "duracion_dias": 30, "fraccion_art226": "IV"}
  ],
  "contiene_psicotropico": false,
  "vigencia_dias": null,
  "qr_verificacion_url": "https://verificar.consultorio.mx/REC-TEL-001",
  "pdf_path": "~/.local/share/plugins-mx/recetas/REC-TEL-001.pdf",
  "firma_medico_aplicada": true
}
```

## Casos edge

- Paciente fuera de México: la farmacia extranjera puede no aceptar receta mexicana y la práctica médica a distancia puede estar regulada por el país del paciente (**verificar**).
- Paciente menor de edad: datos del padre/madre/tutor.
- Renovación de crónicos: requiere nota de evolución de la consulta; el intervalo máximo entre consultas es política clínica del médico, no regla legal.
