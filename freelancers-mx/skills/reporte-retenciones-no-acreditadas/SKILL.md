---
name: reporte-retenciones-no-acreditadas
description: Detecta retenciones de ISR (10% en 612, 1.25% en RESICO PF) e IVA (2/3) que clientes personas morales le hicieron al freelancer y que NO se acreditaron en pagos mensuales ni en la declaración anual. Son pagos a cuenta del freelancer recuperables vía complementaria (dentro de 5 años). Usar cuando el usuario diga retenciones no acreditadas, me retuvieron y no lo declaré, dinero perdido SAT, saldo a favor por retenciones, acreditar retenciones.
allowed-tools: Read, Write
---

# Reporte retenciones no acreditadas

## El problema

Cuando un cliente PM le paga al freelancer, retiene ISR — 10% en actividad profesional 612 (Art. 106 último párrafo LISR) o 1.25% en RESICO PF (Art. 113-J) — y 2/3 del IVA, y los entera al SAT. La retención consta en el propio CFDI de ingreso que emitió el freelancer. El freelancer debe **acreditar** estas retenciones en sus pagos y en la anual. Si no:
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
  "siguiente_paso": "Presentar declaración complementaria con acreditación correcta (dentro de 5 años; revisar con contador)",
  "vigencia_validada": false
}
```
