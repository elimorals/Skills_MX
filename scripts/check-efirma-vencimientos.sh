#!/usr/bin/env bash
# check-efirma-vencimientos.sh
# Mensual día 1 — alerta e.firmas próximas a vencer (90/60/30 días).
set -euo pipefail
SHARE_DIR="${PLUGINS_MX_SHARE_DIR:-$HOME/.local/share/plugins-mx}"
TRACKER="$SHARE_DIR/efirmas-tracker.jsonl"
[ -f "$TRACKER" ] || exit 0
echo "[$(date +%Y-%m-%d)] Check e.firmas próximas a vencer..."
echo "  → /core:efirma-vencimientos para detalle"
