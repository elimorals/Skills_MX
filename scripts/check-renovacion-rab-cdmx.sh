#!/usr/bin/env bash
# check-renovacion-rab-cdmx.sh
# Mensual día 1 — alerta si RAB CDMX (registro anfitriones Airbnb) vence < 60 días.
set -euo pipefail
SHARE_DIR="${PLUGINS_MX_SHARE_DIR:-$HOME/.local/share/plugins-mx}"
TRACKER="$SHARE_DIR/rab-cdmx-registros.jsonl"
[ -f "$TRACKER" ] || exit 0
echo "[$(date +%Y-%m-%d)] Check RAB CDMX vigencias..."
