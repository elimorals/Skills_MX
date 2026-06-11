---
description: Gestiona el flujo de autorización del cliente vía WhatsApp para una cotización pendiente.
argument-hint: "<OT-o-DIAG-folio>"
allowed-tools: Read, Write, Edit, Bash
---

# /talleres:autorizacion

Autorización para: $ARGUMENTS

1. Invoca `autorizacion-cliente-wa`.
2. Identifica estado actual (sin enviar / esperando respuesta / autorizada / sin respuesta).
3. Sugiere siguiente acción:
   - Sin enviar: genera y envía mensaje inicial con cotización + foto/video.
   - Esperando 24h: envía recordatorio amable.
   - Esperando 72h+: envía recordatorio con política de auto detenido.
   - Sin respuesta 5+ días: aplica política de almacenamiento.
4. Si cliente responde con autorización, registra en bitácora con timestamp y dispara `orden-trabajo` para generar OT formal.
5. Si cliente pregunta, ayuda a formular respuesta técnica clara sin presión de venta.
6. Mantiene bitácora auditada en `bitacora-autorizaciones/[diag/ot].json`.
