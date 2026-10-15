---
name: facturacion-paciente-aseguradora
description: Facturación dual de la clínica - al paciente por deducible/coaseguro (CFDI uso D01) y a la aseguradora por convenio de pago directo (CFDI uso G03). Determina el IVA correcto (clínica persona moral = 16%; consulta de médico persona física = exenta), aplica descuento por convenio, concilia pagos de aseguradora a 30-90 días y arma el consolidado mensual. Usar cuando el usuario diga facturar paciente, factura aseguradora, GMM clínica, pago directo aseguradora, deducible y coaseguro, factura hospital.
allowed-tools: Read, Write
---

# Facturación paciente + aseguradora

> Validar con contador. Reglas de CFDI: skill compartida `cfdi-emision`; impuestos: `iva-retenciones-mx`.

## IVA: quién factura importa

| Quién emite | IVA | Fundamento |
|---|---|---|
| Médico persona física (o sociedad civil de médicos) por su consulta/honorario | Exento | Art. 15 fr. XIV LIVA |
| Clínica u hospital **persona moral** (S.A., S.A.P.I.) por consulta, hospitalización, laboratorio, rayos X | **16%** | La exención de fr. XIV es solo PF/SC; la de fr. XV solo para organismos públicos descentralizados |
| Medicamentos facturados por separado | 0% si son medicinas de patente (Art. 2-A fr. I b LIVA) — **verificar** con contador si se cobran dentro del servicio hospitalario |

Entre personas morales (aseguradora → clínica PM) no hay retención de ISR ni IVA por servicios.

## Casos

### A. Sin seguro
- 100% al paciente, CFDI **D01** (gastos hospitalarios / honorarios médicos, deducible si paga por medio no efectivo, Art. 151 fr. I LISR)

### B. Seguro por reembolso
- Paciente paga 100%; CFDI D01 a su nombre para que la aseguradora le reembolse

### C. Convenio de pago directo aseguradora-clínica
- Tarifa de convenio = tarifa lista − descuento pactado
- Paciente paga deducible + coaseguro (el coaseguro se calcula sobre lo que excede el deducible; % según póliza) → CFDI D01
- Aseguradora paga el resto a 30-90 días → CFDI G03 con número de siniestro/folio de autorización

## Ejemplo (clínica persona moral, IVA 16%)

| Concepto | Cálculo | Importe |
|---|---|---|
| Tarifa lista | | $1,500.00 |
| Tarifa convenio (−20%) | 1,500 × 0.80 | $1,200.00 |
| Deducible paciente | | $200.00 |
| Coaseguro paciente 10% | (1,200 − 200) × 10% | $100.00 |
| **Paciente** | 300 + IVA 48 | **$348.00** |
| **Aseguradora** | 900 + IVA 144 | **$1,044.00** |
| Pérdida por descuento | 1,500 − 1,200 | $300.00 |

## Output

```json
{
  "paciente_rfc_hash": "...",
  "aseguradora": "GNP",
  "emisor_tipo": "persona_moral",
  "monto_lista_mxn": "1500.00",
  "descuento_convenio_pct": 0.20,
  "tarifa_convenio_mxn": "1200.00",
  "deducible_paciente_mxn": "200.00",
  "coaseguro_paciente_mxn": "100.00",
  "subtotal_paciente_mxn": "300.00",
  "iva_paciente_mxn": "48.00",
  "total_paciente_mxn": "348.00",
  "subtotal_aseguradora_mxn": "900.00",
  "iva_aseguradora_mxn": "144.00",
  "total_aseguradora_mxn": "1044.00",
  "perdida_descuento_mxn": "300.00",
  "cfdi_paciente_uuid": "...",
  "cfdi_aseguradora_uuid": "...",
  "estado_cobro_aseguradora": "pendiente_45d"
}
```

Si el honorario médico lo factura directamente el médico PF, ese CFDI va sin IVA (exento) y la clínica solo factura su parte.
