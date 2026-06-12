---
name: workflow-dashboard-cartera-semanal
description: Genera dashboard semanal de cartera (vencida, próxima a vencer, top deudores, monto total) para que el freelancer/PyME tenga visibilidad rápida los lunes. Cruza CFDIs emitidos no cobrados, días de vencimiento por cliente, y rankea top 10 deudores. Usar cuando el usuario diga dashboard cartera, status cobranza semanal, cómo va mi cartera, top deudores. NO usar para envío de comunicaciones (eso es cobranza-multinivel).
allowed-tools: Read, Write, Bash
---

# Workflow: Dashboard cartera semanal

Vista ejecutiva de cartera para el lunes en la mañana.

## Trigger

- Cron lunes 09:30 (`scripts/dashboard-semanal.sh`)
- Manual: "dame el dashboard de cartera"

## Fases

### Fase 1 — Cargar CFDIs sin cobro

- `mp_facturama_extendido.listar_cfdis_sin_pago(emisor_rfc)`
- Filtrar tipo I (ingresos) emitidos en últimos 120 días
- Excluir cancelados

### Fase 2 — Calcular vencimiento por cliente

Por cada CFDI:
- Días desde emisión: `today - fecha_cfdi`
- Bucket:
  - `al_corriente`: 0-30 días
  - `vencido_30_60`: 31-60 días
  - `vencido_60_90`: 61-90 días
  - `vencido_90+`: 91+ días (incobrable potencial)

### Fase 3 — Rankear top deudores

Agrupar por `rfc_receptor`, sumar montos pendientes, ordenar descendente.

### Fase 4 — Output

```
═══════════════════════════════════════════════════════════════
  📊 Dashboard cartera — semana del 12 de junio
═══════════════════════════════════════════════════════════════

💰 Total cartera: $385,000 MXN (32 CFDIs)

📅 Por antigüedad:
  ✓ Al corriente (0-30d):    $180,000 (18 CFDIs)
  ⚠ Vencido 30-60d:          $120,000 (8 CFDIs)
  🔴 Vencido 60-90d:          $65,000 (4 CFDIs)
  ⛔ Vencido 90+ días:        $20,000 (2 CFDIs)

🏆 Top 5 deudores (cliente / monto / días promedio):
  1. ACME S.A. de C.V.      $85,000   45 días
  2. Constructora Z         $45,000   62 días
  3. Cliente C              $30,000   28 días
  4. Cliente D              $25,000   72 días
  5. Cliente E              $20,000   95 días

⚠ Acción crítica:
  - Cliente E: 95 días → preparar carta requerimiento legal
  - 2 CFDIs en 90+ → evaluar provisión incobrable contable

✓ Saludable:
  - 47% de cartera al corriente (mes pasado: 38%)
  - Sin clientes en 120+ días
═══════════════════════════════════════════════════════════════
```

### Fase 5 — Persistir

Guardar en `~/.local/share/plugins-mx/dashboards/cartera-<fecha>.json`.

## Dependencias

- `mp_facturama_extendido`
- `mp_bancos_mx` (opcional, para confirmar pagos no registrados)

## ⚠ Compliance

- Nombres de clientes pueden parecer en claro en el dashboard local
- No compartir dashboard fuera del operador
