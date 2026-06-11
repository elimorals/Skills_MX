---
description: Genera Orden de Trabajo formal (inicial, modificación o cierre) con desglose y firmas requeridas.
argument-hint: "<accion: abrir|modificar|cerrar> <OT-folio-o-DIAG>"
allowed-tools: Read, Write, Edit, Bash
---

# /talleres:orden-trabajo

OT: $ARGUMENTS

1. Invoca `orden-trabajo`.
2. Si acción = "abrir":
   - Lee diagnóstico y autorización vinculados.
   - Genera OT-Inicial con todos los trabajos autorizados, desglose, plazo, garantía.
   - Marca campos pendientes de firma cliente y taller.
3. Si acción = "modificar":
   - Lee OT original.
   - Captura nuevo trabajo descubierto + autorización adicional.
   - Genera OT-MOD vinculada.
4. Si acción = "cerrar":
   - Lee OT original.
   - Genera check-out con kilometraje, gasolina, inventario, trabajos completados.
   - Dispara `cfdi-emision` para CFDI.
   - Dispara `garantia-servicio` para certificado.
   - Genera mensaje WhatsApp al cliente confirmando entrega.
5. Guarda en `ordenes-trabajo/[OT-folio]/[fecha]-[accion].md`.
