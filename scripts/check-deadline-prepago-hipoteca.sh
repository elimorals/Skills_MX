#!/usr/bin/env bash
# check-deadline-prepago-hipoteca.sh
# Mensual día 15 — alerta si hay deadline de prepago hipotecario configurado.
set -euo pipefail
SHARE_DIR="${PLUGINS_MX_SHARE_DIR:-$HOME/.local/share/plugins-mx}"
TRACKER="$SHARE_DIR/hipotecas-prepago.jsonl"
[ -f "$TRACKER" ] || exit 0
echo "[$(date +%Y-%m-%d)] Revisar deadlines de prepago hipoteca..."
