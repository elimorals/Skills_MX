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

⚠ Hook `confirmar-envio-masivo-wa` se dispara si > 50 destinatarios.
