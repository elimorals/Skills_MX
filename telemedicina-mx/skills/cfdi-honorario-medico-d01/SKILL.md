---
name: cfdi-honorario-medico-d01
description: Emite CFDI 4.0 de ingreso con uso D01 (honorarios médicos, dentales y gastos hospitalarios) para que el paciente persona física pueda deducir la consulta en su declaración anual (Art. 151 fr. I LISR). Requiere RFC, nombre, régimen y CP del paciente, y pago por medio no efectivo (cheque nominativo, transferencia, tarjeta). Médico persona física: IVA exento (Art. 15 fr. XIV LIVA). Cubre retenciones cuando paga una persona moral (ISR 10% régimen 612 o 1.25% RESICO, sin retención de IVA). Usar cuando el usuario diga facturar consulta, CFDI médico, factura deducible para el paciente, honorario telemedicina, uso D01, factura consulta en línea.
allowed-tools: Read, Write
---

# CFDI honorario médico — uso D01

> Confirmar con contador antes de timbrar. Reglas generales de CFDI: skill compartida `cfdi-emision`; impuestos: `iva-retenciones-mx`.

## Cuándo aplica el uso D01

| Receptor | Uso CFDI |
|---|---|
| Paciente persona física que quiere deducir | **D01** |
| Paciente que no da RFC (público en general `XAXX010101000`) | **S01** (Sin efectos fiscales) — no puede deducir |
| Persona moral (empresa paga por su empleado) | G03 |
| Aseguradora (convenio de pago directo) | G03 |

## Forma de pago y deducibilidad (Art. 151 LISR)

| Forma | Código SAT | ¿Deducible para el paciente? |
|---|---|---|
| Efectivo | 01 | ❌ No |
| Cheque nominativo | 02 | ✅ |
| Transferencia | 03 | ✅ |
| Tarjeta de crédito | 04 | ✅ |
| Tarjeta de débito | 28 | ✅ |
| Tarjeta de servicios | 29 | ✅ |

Si pagó en efectivo se puede emitir D01, pero el paciente no podrá deducir. La deducción también exige que el profesional tenga título registrado; aplica igual a psicología y nutrición (Art. 151 fr. I) y está sujeta al tope global de deducciones personales.

## Impuestos

- **Médico persona física** (612 o RESICO 626): IVA **exento** (Art. 15 fr. XIV LIVA: requiere título de médico y prestarse por PF o sociedad civil). En el CFDI: `ObjetoImp = 02` y traslado IVA con `TipoFactor = "Exento"`, sin tasa ni importe.
- **Psicólogo, nutriólogo u otro profesional no médico**: la exención no los cubre → IVA 16% (confianza media; ver `psicoterapia-mx`).
- **Clínica o plataforma persona moral (S.A.)** que factura la consulta: IVA 16%; la exención es solo para PF/SC.

## Retenciones si quien paga es persona moral (uso G03, no D01)

| Régimen del médico | ISR retenido | IVA retenido |
|---|---|---|
| 612 PFAE | 10% del subtotal | 0 (servicio exento) |
| 626 RESICO PF | 1.25% del subtotal (Art. 113-J LISR) | 0 (servicio exento) |

Ejemplo: consulta $1,200 a una empresa, médico RESICO → ISR retenido 1,200 × 1.25% = $15.00; Total CFDI = 1,200 − 15 = **$1,185.00** (el Total resta retenciones).

## Payload

```python
class CfdiHonorarioMedico(BaseModel):
    tipo_comprobante: Literal["I"] = "I"
    uso_cfdi: Literal["D01", "S01", "G03"] = "D01"
    emisor_rfc: str
    emisor_regimen: Literal["612", "626"]
    receptor_rfc: str              # XAXX010101000 solo con S01
    receptor_nombre: str
    receptor_regimen: str          # p. ej. 605 sueldos, 612, 626
    receptor_cp: str
    forma_pago: Literal["01", "02", "03", "04", "28", "29"]
    metodo_pago: Literal["PUE"] = "PUE"
    clave_prod_serv: str           # familia 8512xxxx (servicios médicos); confirmar la clave exacta en c_ClaveProdServ
    concepto: str                  # "Consulta médica de especialidad (telemedicina) - Cardiología"
    subtotal_mxn: Decimal
    objeto_imp: Literal["02"] = "02"
    iva_tipo_factor: Literal["Exento"] = "Exento"
    total_mxn: Decimal
```

Timbrado: `mp_facturama_extendido` → `facturama_validar_payload_local` y luego `facturama_timbrar_cfdi` (requiere credenciales del PAC del médico; si no las hay, entregar el payload para timbrar en el portal).

## Output

```json
{
  "cfdi_uuid": "abc-123",
  "operation": "cfdi_honorario_medico",
  "modalidad": "telemedicina",
  "paciente_rfc_hash": "...",
  "subtotal_mxn": "1200.00",
  "iva": "Exento",
  "total_mxn": "1200.00",
  "uso_cfdi": "D01",
  "forma_pago": "03",
  "deducible_para_paciente": true,
  "xml_path": "...",
  "pdf_path": "..."
}
```
