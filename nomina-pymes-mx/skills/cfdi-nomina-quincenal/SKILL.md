---
name: cfdi-nomina-quincenal
description: Emite CFDI Nómina 4.0 + Complemento 1.2 Revisión E (vigente desde 29 dic 2025) por cada empleado quincenal. Incluye sueldo bruto + percepciones + deducciones + ISR retenido + IMSS obrero + INFONAVIT + neto a pagar. Validación pre-timbrado del payload (hook pre-timbrado-validation.sh). Art. 99 LISR sin excepción. Usar cuando el usuario diga timbrar nomina, cfdi nomina quincenal, complemento 1.2.
allowed-tools: Read, Write
---

# CFDI Nómina 4.0 + Complemento 1.2 Revisión E

## Estructura

```python
class CfdiNominaPayload(BaseModel):
    # Comprobante
    tipo: Literal["N"] = "N"  # Nómina
    fecha: datetime
    forma_pago: Literal["99"]  # Por definir, nómina especial
    metodo_pago: Literal["PUE"] = "PUE"

    # Emisor (patrón)
    emisor_rfc: str
    emisor_nombre: str
    emisor_regimen: str  # 601 PM, 605 PF, 612 PFAE

    # Receptor (empleado)
    receptor_rfc: str
    receptor_nombre: str
    receptor_curp: str
    receptor_regimen: Literal["605"] = "605"  # Sueldos
    receptor_uso_cfdi: Literal["CN01"] = "CN01"  # Nómina
    receptor_cp: str

    # Concepto único
    concepto: dict

    # Complemento 1.2
    complemento_nomina: NominaComplemento


class NominaComplemento(BaseModel):
    version: Literal["1.2"] = "1.2"
    tipo_nomina: Literal["O", "E"]  # Ordinaria / Extraordinaria
    fecha_pago: date
    fecha_inicial_pago: date
    fecha_final_pago: date
    num_dias_pagados: Decimal

    emisor: EmisorNomina  # registro patronal, curp si PF
    receptor: ReceptorNomina  # NSS, fecha alta IMSS, antigüedad, puesto, etc.

    percepciones: Percepciones  # sueldos + bonos + comisiones + etc.
    deducciones: Deducciones  # ISR + IMSS + INFONAVIT + alimentaria + etc.

    total_percepciones_mxn: Decimal
    total_deducciones_mxn: Decimal
    neto_a_pagar_mxn: Decimal
```

## Validaciones pre-timbrado

1. RFC empleado en padrón SAT (activo)
2. Régimen receptor = 605
3. NSS válido
4. Sueldo > UMA mínimo
5. Forma pago = 99
6. Tipo nómina O o E
7. CP del receptor coincide con CSF

## Output

```json
{
  "uuid": "abc-123",
  "empleado_rfc_hash": "...",
  "periodo": "2026-06-01_2026-06-15",
  "percepciones_total_mxn": "15000.00",
  "deducciones_total_mxn": "2700.50",
  "neto_pagar_mxn": "12299.50",
  "isr_retenido_mxn": "1880.00",
  "imss_obrero_mxn": "320.50",
  "infonavit_descontado_mxn": "500.00",
  "xml_path": "...",
  "pdf_path": "...",
  "complemento_version": "1.2",
  "revision_complemento": "E",
  "vigencia_validada": false
}
```

## ⚠ Errar = multa SAT

Art. 99 LISR sin excepción. Hooks `pre-timbrado-validation.sh` se dispara automáticamente.
