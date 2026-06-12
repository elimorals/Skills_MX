#!/usr/bin/env bash
# check-renovacion-poliza-gmm.sh
# Mensual día 1 — alerta si póliza GMM vence < 90 días.
set -euo pipefail
SHARE_DIR="${PLUGINS_MX_SHARE_DIR:-$HOME/.local/share/plugins-mx}"
TRACKER="$SHARE_DIR/polizas-gmm.jsonl"
[ -f "$TRACKER" ] || exit 0
echo "[$(date +%Y-%m-%d)] Check pólizas GMM próximas a vencer..."
