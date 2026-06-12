---
name: cfdi-servicios-deducible
description: Solicita o registra los CFDIs de los servicios públicos (CFE emite, agua municipal a veces, gas natural emite) para PyME que necesita deducirlos en su contabilidad. CFDIs con uso G03 (gastos en general) o D04 si es casa habitación rentada. Usar cuando el usuario diga cfdi cfe, cfdi servicios deducible, factura electricidad deducir.
allowed-tools: Read, Write
---

# CFDI servicios deducibles

## Qué CFDI emite cada uno

| Servicio | Emite CFDI | Uso CFDI sugerido |
|---|---|---|
| CFE | ✅ Sí, vía CFE Mi Mexicana | G03 (general) o D04 (residencial) |
| Agua | A veces (depende municipio) | G03 |
| Gas natural | ✅ Sí | G03 |
| Predial | Solo recibo, NO CFDI | NA |
| Gas LP | ✅ Sí | G03 |

## Para PyME (deducible 100%)

Los gastos de servicios públicos son 100% deducibles si:
- CFDI a nombre de la PyME
- Forma pago no efectivo
- Uso G03 (gastos en general)
- Servicio en domicilio fiscal de la PyME

## Para PF en RESICO PF (NO deducible)

Régimen 626 no permite deducciones acumulables.

## Para arrendador (parcialmente deducible)

Si arrendador paga la luz/agua de propiedad rentada y NO se la cobra al inquilino:
- Deducible en su declaración de arrendamiento

## Output

```json
{
  "ejercicio": 2026,
  "mes": "06",
  "cfdis_recopilados": [
    {"servicio": "cfe", "uuid": "...", "monto_mxn": "4250.00", "uso": "G03"},
    {"servicio": "gas_natural", "uuid": "...", "monto_mxn": "620.00", "uso": "G03"}
  ],
  "total_deducible_mxn": "4870.00"
}
```
