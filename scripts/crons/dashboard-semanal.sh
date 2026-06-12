#!/usr/bin/env bash
# dashboard-semanal.sh
# Cron lunes 09:00: dashboard semanal de KPIs operativos.
#
# Genera reporte con: cartera vencida, cierres pendientes, vencimientos próximos,
# alertas críticas no resueltas, sesiones de Claude de la semana.

set -euo pipefail

REPO="${PATH_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
SEMANA=$(date +%Y-W%V)
OUT_DIR="$REPO/dashboards/$SEMANA"
mkdir -p "$OUT_DIR"

OUT_FILE="$OUT_DIR/dashboard.md"

cat > "$OUT_FILE" <<EOF
# Dashboard semanal $SEMANA

**Generado**: $(date -Iseconds)

## KPIs operativos

| Métrica | Valor |
|---|---|
| Cartera vencida total | (pendiente leer cobranza/.../) |
| Facturas emitidas semana pasada | (pendiente contar cfdi/.../*.json) |
| CFDIs por cobrar PPD | (pendiente filtrar) |
| Alertas críticas no resueltas | (pendiente leer alertas/) |

## Próximos vencimientos (7 días)

- Pólizas seguros: (pendiente cartera-polizas/)
- Pagos provisionales: día 15 / 17
- Cierre fiscal mensual: día 14
- Renovaciones contratos: (pendiente)
- e.firma del usuario: (pendiente mp_sat_portal.verificar_efirma_vigente)

## Recomendaciones IA

1. Revisar alertas críticas pendientes
2. Procesar cobranza-multinivel si hay morosos > 30 días
3. Validar e.firma vigencia si quedan < 30 días

## Sesiones Claude últimos 7 días

(pendiente integración con persisted-output / .remember/)
EOF

echo "$(date -Iseconds) - Dashboard semanal generado: $OUT_FILE"
