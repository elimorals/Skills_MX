---
name: cfdi-honorario-medico-d01
description: Emite CFDI tipo I con uso D01 (Honorarios médicos, dentales y gastos hospitalarios) para que el paciente pueda deducir el pago en su declaración anual Art. 151 LISR. Requiere RFC del paciente y forma de pago no efectivo. Si el paciente paga en efectivo, NO podrá deducir aunque el CFDI sea D01. Usar cuando el usuario diga facturar consulta, cfdi medico, deducible paciente, honorario telemedicina.
allowed-tools: Read, Write
---

# CFDI honorario médico — uso D01

## Cuándo aplica el uso D01

| Receptor | Aplica D01 |
|---|---|
| Persona física (paciente) | ✅ Sí — puede deducir si paga no-efectivo |
| Persona moral (empresa por su empleado) | ❌ No — usar G03 |
| Aseguradora (convenio directo) | ❌ No — usar G03 |

## Forma de pago crítica

| Forma | Código SAT | Deducible para paciente? |
|---|---|---|
| Efectivo | 01 | ❌ **NO deducible** |
| Cheque | 02 | ✅ Sí |
| Transferencia SPEI | 03 | ✅ Sí |
| Tarjeta crédito | 04 | ✅ Sí |
| Tarjeta débito | 28 | ✅ Sí |

⚠ Aunque emitas CFDI D01, si pagó EN EFECTIVO el paciente NO podrá deducir (Art. 151 LISR + reglas SAT).

## Payload CFDI

```python
class CfdiHonorarioMedico(BaseModel):
    tipo_comprobante: Literal["I"] = "I"
    uso_cfdi: Literal["D01"] = "D01"
    emisor_rfc: str  # del médico
    emisor_regimen: Literal["612", "626"]  # PFAE o RESICO PF
    receptor_rfc: str  # del paciente (no XAXX si quiere deducir)
    receptor_nombre: str
    receptor_cp: str
    forma_pago: Literal["02", "03", "04", "28"]  # NO 01
    metodo_pago: Literal["PUE"] = "PUE"  # consulta pagada al momento
    concepto: str  # "Consulta médica especializada - Cardiología"
    subtotal_mxn: Decimal
    iva_traslado_mxn: Decimal = Decimal("0")  # médicos PF: exento IVA
    total_mxn: Decimal
```

## Caso especial: paciente con RFC genérico

Si paciente no quiere dar RFC (paga consulta pero no necesita deducir):
- Usar `XAXX010101000` (público en general)
- Uso CFDI `S01` (Sin efectos fiscales) o `D01`
- Paciente NO podrá deducir
- Aún cumple obligación fiscal del médico (debe emitir CFDI)

## Output

```json
{
  "cfdi_uuid": "abc-123",
  "operation": "cfdi_honorario_medico",
  "modalidad": "telemedicina",
  "paciente_rfc_hash": "...",
  "monto_consulta_mxn": "1200.00",
  "iva_mxn": "0.00",
  "total_mxn": "1200.00",
  "uso_cfdi": "D01",
  "forma_pago": "03",
  "deducible_para_paciente": true,
  "xml_path": "...",
  "pdf_path": "..."
}
```

## ⚠ Médico en RESICO PF (626)

- IVA: exento (no se traslada al paciente)
- Tasa retención si paciente PM: 1.25% del subtotal (no 10%)
- Mismas reglas D01 + forma pago
