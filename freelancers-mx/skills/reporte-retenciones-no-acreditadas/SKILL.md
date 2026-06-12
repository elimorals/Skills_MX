---
name: reporte-retenciones-no-acreditadas
description: Detecta retenciones de ISR que clientes PM le hicieron al freelancer (PF 612 PFAE) y que NO se acreditaron en pagos provisionales ni en la declaración anual previa. Estas retenciones son DINERO del freelancer que se quedó con SAT — recuperable como saldo a favor. Usar cuando el usuario diga retenciones no acreditadas, dinero perdido sat, saldo favor por retenciones.
allowed-tools: Read, Write
---

# Reporte retenciones no acreditadas

## El problema

Cuando un cliente PM le paga al freelancer, retiene 10% ISR (Art. 116 LISR) y lo entera al SAT. El freelancer debe **acreditar** estas retenciones en su declaración anual. Si no:
- Pagó más impuesto del que debió
- Tiene saldo a favor recuperable

## Patrón típico de error

- Freelancer no lleva listado de CFDIs con retención
- Captura solo monto neto recibido (no monto retenido)
- En anual no acredita las retenciones del año
- Pierde dinero (típico $5,000-$50,000 MXN)

## Output

```json
{
  "rfc_hash": "...",
  "ejercicio_revisado": 2025,
  "cfdis_con_retencion_isr": 23,
  "monto_retencion_isr_total_mxn": "28500.00",
  "retenciones_acreditadas_declaracion": "12000.00",
  "retenciones_NO_acreditadas_mxn": "16500.00",
  "recuperable_via_complementaria": true,
  "ahorro_si_se_corrige_mxn": "16500.00",
  "siguiente_paso": "Presentar declaración complementaria con acreditación correcta"
}
```
