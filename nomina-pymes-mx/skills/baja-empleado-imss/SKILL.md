---
name: baja-empleado-imss
description: Baja de empleado ante el IMSS con aviso IDSE en 5 días hábiles (Arts. 15 fr. I y 37 LSS) y cálculo de finiquito (salarios devengados, aguinaldo, vacaciones y prima vacacional proporcionales) o liquidación por despido injustificado (3 meses de salario integrado, 20 días por año cuando aplica, prima de antigüedad de 12 días por año topada a 2 salarios mínimos, Art. 162 LFT). Incluye exención ISR de 90 UMA por año. Usar cuando el usuario diga baja empleado, despido, renuncia, terminación laboral, finiquito, liquidación, indemnización, prima de antigüedad.
allowed-tools: Read, Write
---

# Baja de empleado (IMSS + finiquito/liquidación)

## Tipos de terminación

| Caso | Paga | Notas |
|---|---|---|
| A. Renuncia voluntaria | Finiquito | Prima de antigüedad solo si tiene **15 años o más** (Art. 162 fr. III). Carta de renuncia firmada. |
| B. Despido justificado (Art. 47 LFT) | Finiquito + prima de antigüedad | Entregar **aviso de rescisión** por escrito al trabajador o vía el Tribunal dentro de 5 días hábiles; sin aviso se presume injustificado. |
| C. Despido injustificado | Finiquito + indemnización constitucional **3 meses** (Art. 48) + prima de antigüedad + salarios caídos si hay juicio (máx. 12 meses, luego interés 2% mensual sobre 15 meses) | Los **20 días por año** (Art. 50 fr. II) proceden cuando el patrón se niega a reinstalar (Art. 49) o el trabajador rescinde por causa del patrón (Art. 52); en convenios suele incluirse. |
| D. Mutuo acuerdo / convenio | Lo pactado (no puede renunciar a derechos devengados, Art. 33) | Ratificar ante el **Centro de Conciliación** (federal o local) o el Tribunal Laboral; la STPS ya no ratifica convenios desde la reforma de 2019. |
| E. Defunción | Finiquito + prima de antigüedad a beneficiarios (Art. 501) | Más prestaciones del IMSS a beneficiarios. |

Las indemnizaciones (Art. 48, 50) se calculan con **salario integrado** (Art. 84, 89 LFT). La prima de antigüedad usa el salario con **tope de 2 salarios mínimos** (Arts. 162, 485, 486): 2 × $315.04 = **$630.08** ($881.74 en ZLFN) en 2026. Se paga proporcional por fracción de año, sin mínimo de antigüedad (salvo renuncia).

## Aviso al IMSS

- Aviso de baja en **5 días hábiles** (Art. 15 fr. I LSS) vía IDSE o `imss_enviar_movimiento_afiliatorio` de `mp_imss_patronal` (estado "sin verificar"; confirma el acuse en IDSE).
- Mientras no se presente, el patrón sigue causando cuotas (Art. 37 LSS).
- Si el trabajador tiene crédito INFONAVIT, avisa también la suspensión del descuento.

## Algoritmo de finiquito

```python
def finiquito(salario_diario: D, fecha_baja: date, inicio_computo: date,
              vac_pendientes: int, dias_pendientes_pago: int) -> dict:
    # inicio_computo = 1-ene del año o la fecha de alta si fue en el mismo año
    dias = (fecha_baja - inicio_computo).days + 1
    aguinaldo = salario_diario * 15 * dias / 365
    vacaciones = salario_diario * vac_pendientes  # incluye proporcional del año en curso
    prima_vac = vacaciones * D("0.25")
    devengado = salario_diario * dias_pendientes_pago
    return {...}
```

## Exenciones ISR

- Indemnización, prima de antigüedad y demás pagos por separación: exentos hasta **90 UMA por año de servicio** (Art. 93 fr. XIII LISR) = $10,557.90 por año (2026); el excedente se grava con el procedimiento del Art. 96 últimos párrafos.
- Aguinaldo proporcional: 30 UMA; prima vacacional: 15 UMA (Art. 93 fr. XIV).

## Output

```json
{
  "empleado_id_hash": "...",
  "fecha_baja": "2026-06-15",
  "tipo": "renuncia_voluntaria",
  "antiguedad_anos": 2.5,
  "finiquito_mxn": "<calculado>",
  "indemnizacion_mxn": "0.00",
  "prima_antiguedad_mxn": "0.00",
  "aviso_idse_pendiente": true,
  "deadline_idse": "2026-06-22",
  "cfdi_nomina_finiquito_pendiente": true,
  "vigencia_validada": false
}
```

En renuncia con menos de 15 años la prima de antigüedad es 0; en despido sería 12 × min(salario, $630.08) × 2.5 años.

## ⚠ Documentos y validación

- Carta de renuncia (A), aviso de rescisión (B), convenio ratificado (D), acta de defunción y designación de beneficiarios (E).
- Recibo de finiquito firmado y CFDI de nómina (percepciones 022 prima por antigüedad, 023 pagos por separación, 025 indemnizaciones).
- Despidos y convenios tienen riesgo litigioso: revisa con abogado laboral y contador antes de pagar.
