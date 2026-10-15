---
name: cfdi-nomina-quincenal
description: Arma y valida el CFDI de Nómina 4.0 con Complemento de Nómina 1.2 (revisión E, obligatoria desde 2026) por empleado y quincena - percepciones gravadas/exentas, deducciones (ISR retenido, IMSS obrero, INFONAVIT, pensión alimenticia), subsidio causado en OtrosPagos y neto a pagar. Validación pre-timbrado del payload (hook pre-timbrado-validation.sh). Obligación del Art. 99 fr. III LISR. Usar cuando el usuario diga timbrar nómina, CFDI de nómina, recibo de nómina, cfdi nomina quincenal, complemento de nómina 1.2, revisión E.
allowed-tools: Read, Write
---

# CFDI Nómina 4.0 + Complemento Nómina 1.2 (rev. E)

Estructura base del CFDI y catálogos: ver skill `cfdi-emision` de `core-mexico` (`references/complementos-cfdi.md`, sección Nómina 1.2).

Revisión E del complemento: el SAT publicó en diciembre 2025 el estándar, XSD, catálogos y matriz de errores; aplica a nóminas de 2026 (fuentes secundarias: El Conta, ContadorMX; confianza media). Cambios reportados: el error 75 exige `ImporteGravado` > 0 cuando `ImporteExento` = 0 y el tope de validación del subsidio causado subió (reportado $628.00). Verifica la matriz de errores vigente en el portal del SAT.

## Estructura

```python
class CfdiNominaPayload(BaseModel):
    tipo: Literal["N"] = "N"
    fecha: datetime
    forma_pago: Literal["99"] = "99"      # Por definir (regla de nómina)
    metodo_pago: Literal["PUE"] = "PUE"
    exportacion: Literal["01"] = "01"
    emisor_rfc: str
    emisor_regimen: str                   # 601 PM, 612 PF con actividad, etc.
    receptor_rfc: str
    receptor_nombre: str                  # exacto como en la CSF
    receptor_regimen: Literal["605"] = "605"
    receptor_uso_cfdi: Literal["CN01"] = "CN01"
    receptor_cp: str                      # CP de la CSF
    concepto: dict                        # ClaveProdServ 84111505, ClaveUnidad ACT, cantidad 1
    complemento_nomina: "NominaComplemento"

class NominaComplemento(BaseModel):
    version: Literal["1.2"] = "1.2"
    tipo_nomina: Literal["O", "E"]        # Ordinaria / Extraordinaria
    fecha_pago: date
    fecha_inicial_pago: date
    fecha_final_pago: date
    num_dias_pagados: Decimal
    emisor: dict          # RegistroPatronal (y Curp si el patrón es PF)
    receptor: dict        # Curp, NSS, FechaInicioRelLaboral, Antigüedad, TipoContrato, TipoJornada,
                          # TipoRegimen 02, PeriodicidadPago "04" (quincenal), SBC, SDI, ClaveEntFed
    percepciones: list    # 001 sueldo, 002 aguinaldo, 019 horas extra, 021 prima vacacional...
    deducciones: list     # 001 seguridad social, 002 ISR, 007 pensión alimenticia, 010 INFONAVIT...
    otros_pagos: list     # 002 subsidio para el empleo (con SubsidioCausado), aunque sea 0 a pagar
```

## Validaciones pre-timbrado

1. RFC, nombre y CP del receptor coinciden con su CSF (`sat_consultar_padron` si está disponible).
2. Régimen receptor 605, uso CN01, forma de pago 99, método PUE.
3. NSS y registro patronal presentes cuando hay relación laboral (TipoRegimen 02).
4. Salario diario ≥ salario mínimo ($315.04 / $440.87 ZLFN 2026).
5. Cada percepción separa gravado/exento según Art. 93 LISR; ISR calculado con `calculo-isr-salarios-art96`.
6. Subsidio: solo si ingresos del mes ≤ $11,492.66; nunca mayor que el ISR causado.
7. Totales: neto = total percepciones + otros pagos − total deducciones.

## Ejemplo recalculado

Sueldo quincenal $15,000 (diario $1,000; SBC 1,049.30): ISR $2,259.83 (tarifa 2026 mensualizada), IMSS obrero 15 días $415.66, descuento INFONAVIT $500.00 (según aviso).
Deducciones = 2,259.83 + 415.66 + 500.00 = **$3,175.49**; neto = **$11,824.51**.

```json
{
  "uuid": "<asignado por el PAC>",
  "empleado_rfc_hash": "...",
  "periodo": "2026-06-01_2026-06-15",
  "percepciones_total_mxn": "15000.00",
  "deducciones_total_mxn": "3175.49",
  "neto_pagar_mxn": "11824.51",
  "isr_retenido_mxn": "2259.83",
  "imss_obrero_mxn": "415.66",
  "infonavit_descontado_mxn": "500.00",
  "complemento_version": "1.2",
  "revision_complemento": "E",
  "vigencia_validada": false
}
```

## ⚠ Plazo y sanción

- Emitir el CFDI de nómina es requisito de deducibilidad del salario (Art. 27 fr. V y 99 fr. III LISR). Plazo de emisión: regla de nómina de la RMF 2026 (antes del pago o dentro del plazo que fije la regla vigente; **verificar** número y texto de la regla en la RMF 2026).
- El hook `pre-timbrado-validation.sh` revisa el payload antes de enviarlo al PAC; no reemplaza la validación del PAC ni la revisión del contador.
