---
name: alertas-vencimientos-pagos
description: Genera alertas escalonadas (T-7, T-3, T-1, vencido) para facturas de servicios próximas a vencer. Distingue impacto: CFE corte de luz, agua corte servicio, predial intereses moratorios. Usar cuando el usuario diga alertas vencimientos servicios, recordatorios pago servicios.
allowed-tools: Read, Write
---

# Alertas vencimientos pagos

## Niveles

| Estado | Días vs deadline | Severidad |
|---|---|---|
| Normal | > 7 días | 🟢 verde |
| Próximo | 3-7 días | 🟡 amarillo |
| Urgente | 1-2 días | 🟠 naranja |
| Hoy | 0 días | 🔴 rojo |
| Vencido | < 0 días | ⛔ crítico |

## Impacto por servicio

| Servicio | Consecuencia del atraso (confirmar en el recibo o reglamento local) |
|---|---|
| CFE | Puede suspender el suministro después de la fecha límite; el recibo trae la fecha de corte. Reconexión con cargo |
| Agua | Según la ley local: restricción o suspensión del servicio + recargos. En uso doméstico varias entidades solo permiten restringir, no cortar |
| Predial | Actualización + recargos mensuales según el código fiscal local; se pierde el descuento por pago anticipado |
| Gas natural | Suspensión según el contrato del distribuidor + cargo de reconexión |

No inventes plazos de corte ni tasas de recargo: toma la fecha límite y la de corte del recibo. Si el recibo no la trae, di "verificar con el proveedor".

## Output

```json
{
  "alertas_activas": 3,
  "items": [
    {"servicio": "gas_natural", "deadline": "2026-06-15", "monto_mxn": "620", "severidad": "naranja", "dias_restantes": 3},
    {"servicio": "cfe", "deadline": "2026-06-18", "monto_mxn": "4250", "severidad": "amarillo", "dias_restantes": 6}
  ]
}
```
