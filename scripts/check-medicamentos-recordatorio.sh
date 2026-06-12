#!/usr/bin/env bash
# check-medicamentos-recordatorio.sh
# Cada hora durante el día — verifica si toca tomar medicamento crónico.
set -euo pipefail
SHARE_DIR="${PLUGINS_MX_SHARE_DIR:-$HOME/.local/share/plugins-mx}"
TRACKER="$SHARE_DIR/medicamentos-cronicos.jsonl"
[ -f "$TRACKER" ] || exit 0
hora_actual=$(date +%H:%M)
echo "[$hora_actual] Check medicamentos a tomar ahora..."
