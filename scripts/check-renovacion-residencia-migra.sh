#!/usr/bin/env bash
# check-renovacion-residencia-migra.sh
# Mensual día 1 — alerta si residencia INM vence < 90 días.
set -euo pipefail
SHARE_DIR="${PLUGINS_MX_SHARE_DIR:-$HOME/.local/share/plugins-mx}"
TRACKER="$SHARE_DIR/residencia-migra.jsonl"
[ -f "$TRACKER" ] || exit 0
echo "[$(date +%Y-%m-%d)] Check residencias migra próximas a vencer..."
