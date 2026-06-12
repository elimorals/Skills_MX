#!/usr/bin/env bash
# alerta-pago-provisional.sh
# Cron día 15 de cada mes 10:00: alerta WhatsApp "hoy es el día del pago provisional".
#
# Lee fiscal/<mes>/pago-provisional.md generado por cierre-fiscal-mensual.
# Envía WhatsApp al usuario con resumen + link de DeclaraSAT.

set -euo pipefail

REPO="${PATH_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
MES=$(date +%Y-%m)
PAGO_FILE="$REPO/fiscal/$MES/pago-provisional.md"

if [ ! -f "$PAGO_FILE" ]; then
  echo "$(date -Iseconds) - ALERTA: $PAGO_FILE no existe — workflow cierre-fiscal-mensual no se ha corrido este mes"
  # Auto-trigger del workflow sería ideal aquí. Por ahora, solo alerta al usuario.
  exit 1
fi

# Aquí va invocación a Meta WhatsApp Cloud API (mp_meta_whatsapp_cloud)
# Por ahora genera un archivo de alerta para que el usuario lo vea al abrir Claude Code
mkdir -p "$REPO/alertas/$(date +%Y-%m-%d)"
cat > "$REPO/alertas/$(date +%Y-%m-%d)/pago-provisional-hoy.md" <<EOF
# 🚨 HOY: día del pago provisional

Mes: $MES
Reporte: $PAGO_FILE

Acciones:
1. Revisar el reporte de cierre fiscal
2. Generar línea de captura en https://www.sat.gob.mx
3. Realizar pago antes del día 17

Si no se hace en plazo: recargos + actualización + posible multa.
EOF

echo "$(date -Iseconds) - Alerta pago provisional generada"
