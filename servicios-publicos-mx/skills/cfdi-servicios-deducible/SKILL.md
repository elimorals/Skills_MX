---
name: cfdi-servicios-deducible
description: Recopila y revisa los CFDI de servicios públicos (CFE, agua, gas natural, gas LP, predial) para que una PyME, persona física con actividad empresarial o arrendador los deduzca y acredite el IVA. Indica uso de CFDI G03, requisitos de deducibilidad (Art. 27 LISR) y cuándo no son deducibles (RESICO PF, consumo de casa habitación personal). Usar cuando el usuario diga cfdi cfe, factura de luz, cfdi servicios deducible, factura electricidad deducir, deducir agua o gas, facturar recibo de luz.
allowed-tools: Read, Write
---

# CFDI de servicios deducibles

## Qué comprobante emite cada uno

| Servicio | Comprobante | Uso CFDI |
|---|---|---|
| CFE | CFDI (descarga en el portal de CFE con el número de servicio/RPU) | G03 |
| Agua | Depende del organismo operador: unos emiten CFDI, otros solo recibo | G03 |
| Gas natural | CFDI del distribuidor | G03 |
| Gas LP | CFDI del distribuidor (pedirlo al pagar) | G03 |
| Predial | Depende de la tesorería: varias emiten CFDI, otras solo recibo oficial | G03 |

No existe un uso de CFDI de "deducción personal" para luz, agua o gas: el consumo de la casa propia no es deducción personal (Art. 151 LISR). **D04 es "Donativos"**, nunca lo uses para servicios.

## Cuándo son deducibles

**PM y PF con actividad empresarial o profesional** (régimen general): deducibles si son estrictamente indispensables para la actividad (Art. 27 fr. I LISR) y:
- CFDI a nombre del contribuyente, con su RFC y régimen.
- Pagos mayores a $2,000 con transferencia, cheque nominativo o tarjeta, no efectivo (Art. 27 fr. III LISR).
- Servicio en un inmueble usado para la actividad. Si el inmueble es mixto (casa-oficina), deduce solo la proporción que puedas sustentar.
- El IVA trasladado es acreditable en la misma proporción (Art. 5 LIVA).

**RESICO PF (626)**: no deduce; paga ISR sobre ingresos cobrados (Art. 113-E LISR). Recopilar CFDI solo sirve para control.

**RESICO PM**: sí deduce gastos estrictamente indispensables con CFDI.

**Arrendador PF**: si paga la luz o el agua del inmueble rentado y no se la cobra al inquilino, puede deducirla con deducciones reales; si eligió la deducción ciega del 35%, no deduce nada más que el predial (Art. 115 LISR).

## Flujo

1. Por cada servicio del mes, pide el CFDI (XML) o el recibo.
2. Revisa RFC receptor, uso G03, forma de pago y que el UUID esté vigente (`sat_verificar_cfdi_uuid`, `mp_sat_portal`).
3. Clasifica deducible / no deducible / proporcional según el régimen.
4. Suma subtotal e IVA por separado.

## Output

```json
{
  "ejercicio": 2026,
  "mes": "06",
  "regimen": "601",
  "cfdis_recopilados": [
    {"servicio": "cfe", "uuid": "...", "subtotal_mxn": "3663.79", "iva_mxn": "586.21", "total_mxn": "4250.00", "uso": "G03", "deducible": true},
    {"servicio": "gas_natural", "uuid": "...", "subtotal_mxn": "534.48", "iva_mxn": "85.52", "total_mxn": "620.00", "uso": "G03", "deducible": true}
  ],
  "total_deducible_mxn": "4198.27",
  "iva_acreditable_mxn": "671.73"
}
```

Cálculo: 4,250 / 1.16 = 3,663.79 (IVA 586.21); 620 / 1.16 = 534.48 (IVA 85.52). Deducible = 3,663.79 + 534.48 = 4,198.27; IVA acreditable = 586.21 + 85.52 = 671.73.

## Advertencias

- La deducibilidad depende del régimen y de la actividad; valida con tu contador.
- Para emitir o revisar CFDI a detalle usa `cfdi-emision` (core-mexico).
