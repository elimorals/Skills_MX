---
name: receta-electronica-tele-cofepris
description: Emite receta electrónica para consulta remota con cumplimiento COFEPRIS y NOM-024-SSA3-2010. Incluye e.firma del médico, datos del paciente, diagnóstico CIE-10, medicamentos con genérico+dosis+duración, indicaciones. BLOQUEO AUTOMÁTICO si receta incluye sustancia controlada Grupos I-II (estos siguen requiriendo recetario físico con código de barras hasta piloto 2027 COFEPRIS). Usar cuando el usuario diga receta tele, prescripcion remota, prescribir online.
allowed-tools: Read, Write
---

# Receta electrónica telemedicina + COFEPRIS

## Validaciones obligatorias

1. **Cédula profesional médico vigente** (validar contra SEP)
2. **e.firma del médico vigente** (no vencida)
3. **Paciente identificable** (RFC, CURP o ID gobierno)
4. **Sin medicamentos Grupos I-II** (bloqueo hard)
5. **Diagnóstico CIE-10 presente** (sin diagnóstico → no receta)

## Catálogo bloqueante por grupo

```python
GRUPOS_BLOQUEADOS_TELE = {1, 2}  # opioides + estupefacientes
GRUPOS_PERMITIDOS_TELE = {3, 4, 5}  # psicotrópicos III + antibióticos + otros

# Algunos medicamentos comunes Grupo III (alprazolam, diazepam, clonazepam):
# Permitidos en receta digital DESDE el piloto 2026 COFEPRIS.
# Antes de 2026 también requerían receta física.
```

## Algoritmo

```python
def emitir_receta_tele(medicamentos: list[Medicamento]) -> RecetaResult:
    # 1. Validar cédula médico vigente
    if not validar_cedula_sep_vigente(medico.cedula):
        return error("Cédula no vigente — actualizar antes")

    # 2. Validar e.firma
    if not medico.efirma_vigente():
        return error("e.firma vencida o sin cargar")

    # 3. Validar grupos
    grupos_en_receta = {m.grupo_cofepris for m in medicamentos}
    if GRUPOS_BLOQUEADOS_TELE & grupos_en_receta:
        return error(
            "RECETA_FISICA_REQUERIDA",
            "Contiene Grupo I/II — usar recetario físico con código de barras"
        )

    # 4. Firmar electrónicamente
    pdf = generar_pdf_receta(medicamentos, paciente, diagnostico)
    pdf_firmado = firmar_con_efirma(pdf, medico.efirma)

    # 5. Generar QR de verificación
    qr_url = registrar_y_obtener_qr(receta_id)

    return RecetaResult(
        receta_id=receta_id,
        pdf_path=pdf_firmado,
        qr_url=qr_url,
        contiene_controlado=any(m.grupo_cofepris == 3 for m in medicamentos),
        valido_por_dias=90  # estándar
    )
```

## QR de verificación

Cada receta tiene un QR que permite a la farmacia validar:
- Receta auténtica (firma médico)
- No alterada
- No expirada
- No usada (la primera farmacia que dispensa la marca como usada)

## Output

```json
{
  "receta_id": "REC-TEL-001",
  "fecha_emision": "2026-06-12T16:30:00",
  "modalidad": "telemedicina",
  "medico_cedula": "1234567",
  "paciente_rfc_hash": "...",
  "diagnostico_cie10": "I10",
  "medicamentos": [
    {"generico": "Losartán", "presentacion": "50mg tab", "dosis": "1 cada 24h", "duracion_dias": 30}
  ],
  "contiene_controlado_grupo3": false,
  "valido_hasta": "2026-09-12",
  "qr_verificacion_url": "https://verificar.consultorio.mx/REC-TEL-001",
  "pdf_path": "~/.local/share/plugins-mx/recetas/REC-TEL-001.pdf",
  "firma_medico_aplicada": true
}
```

## Casos edge

- Paciente fuera de MX (USA) → puede que farmacia local no acepte receta MX
- Paciente menor de edad → datos del padre/tutor en la receta
- Refill (renovación de medicamento crónico) → permitido si < 30 días desde última consulta documentada
