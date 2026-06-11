---
description: Emite CFDI de colegiatura mensual con UsoCFDI D10 y complemento InsEduc para deducibilidad del padre.
argument-hint: "<familia> <mes>"
allowed-tools: Read, Write, Edit, Bash
---

# /colegios:facturar-colegiatura

CFDI de colegiatura: $ARGUMENTS

1. Invoca `cfdi-colegiaturas-deducibles`.
2. Lee datos del alumno y padre desde `clientes/[familia]/ficha.json`.
3. Valida RFCs (padre + colegio) con `rfc-validacion`.
4. Confirma exención de IVA con `iva-retenciones-mx`.
5. Verifica que la forma de pago efectivamente recibida sea electrónica (03/04/28/02 — no 01 efectivo).
6. Construye payload CFDI con UsoCFDI D10 y complemento InsEduc completo (alumno, CURP, nivel, autoRVOE, rfcPago).
7. Aplica `cfdi-emision` para timbrado (mock por default).
8. Guarda XML + PDF en `cfdi/[familia]/[mes]-[alumno]-[folio].xml`.
9. Alertas críticas:
   - Si forma de pago = efectivo: avisa que el padre NO podrá deducir.
   - Si está cerca del tope anual deducible: estimación.
10. Si es diciembre o cierre de ciclo: ofrece generar constancia anual de servicios educativos para todo el ejercicio.
11. Notifica al padre via WhatsApp template `utility_cfdi_colegiatura_listo_mx` con el link de descarga.
