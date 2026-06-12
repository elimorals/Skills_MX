#!/usr/bin/env bash
# check-renovacion-rvoe-escuelas.sh
# Mensual día 1 — alerta RVOE próximo a vencer en escuelas registradas.
set -euo pipefail
SHARE_DIR="${PLUGINS_MX_SHARE_DIR:-$HOME/.local/share/plugins-mx}"
TRACKER="$SHARE_DIR/rvoe-escuelas.jsonl"
[ -f "$TRACKER" ] || exit 0
echo "[$(date +%Y-%m-%d)] Check RVOE escuelas próximas a vencer..."
