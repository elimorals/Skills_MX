---
name: comunicacion-clientes-batch
description: Envío de comunicaciones masivas a clientes del despacho por WhatsApp o email (avisos reformas fiscales, recordatorios documentos, fechas críticas). Respeta opt-in LFPDPPP y umbral 50 destinatarios (hook confirma-envio-masivo-wa). Usar cuando el usuario diga avisar a todos los clientes, comunicacion masiva, reforma fiscal aviso.
allowed-tools: Read, Write
---

# Comunicación masiva clientes

## Casos de uso

- Reforma fiscal anunciada (impacto a clientes)
- Recordatorio entregar CFDIs del mes
- Cambio de tarifa del despacho
- Promoción servicio adicional (declaración anual)

## Output

```json
{
  "campaña_id": "AVISO-2026-06-FISCAL",
  "destinatarios": 47,
  "canal_default": "whatsapp",
  "plantilla_usada": "reforma_fiscal_aviso_2026_06",
  "enviados_ok": 45,
  "fallidos": 2,
  "razones_fallo": ["numero_invalido", "no_opt_in"]
}
```

⚠ El hook `confirmar-envio-masivo-wa` emite una advertencia (no bloquea) si hay más de 50 destinatarios (umbral configurable con `PLUGINS_MX_WA_BATCH_UMBRAL`). Confirma con el usuario antes de enviar.

- WhatsApp fuera de la ventana de 24 h solo con plantillas aprobadas por Meta; Meta cobra por mensaje entregado (desde 01-07-2025) según la categoría (marketing/utility). Ver skill `whatsapp-business-mx`.
- Avisos de reformas: cita la fuente (DOF/RMF) y fecha; no anuncies cambios no publicados como vigentes.
