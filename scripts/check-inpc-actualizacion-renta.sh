#!/usr/bin/env bash
# check-inpc-actualizacion-renta.sh
# Mensual día 1 — verifica si alguna propiedad arrendada requiere actualización INPC (aniversario).
set -euo pipefail
SHARE_DIR="${PLUGINS_MX_SHARE_DIR:-$HOME/.local/share/plugins-mx}"
TRACKER="$SHARE_DIR/propiedades-arrendamiento.jsonl"
[ -f "$TRACKER" ] || exit 0
echo "[$(date +%Y-%m-%d)] Check actualizaciones INPC arrendamiento..."
