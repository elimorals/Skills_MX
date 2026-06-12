#!/usr/bin/env bash
# check-vencimiento-contratos-arrendamiento.sh
# Mensual día 1 — alerta contratos próximos a vencer < 60 días (iniciar renovación o nuevo inquilino).
set -euo pipefail
SHARE_DIR="${PLUGINS_MX_SHARE_DIR:-$HOME/.local/share/plugins-mx}"
TRACKER="$SHARE_DIR/contratos-arrendamiento.jsonl"
[ -f "$TRACKER" ] || exit 0
echo "[$(date +%Y-%m-%d)] Check contratos arrendamiento próximos a vencer..."
