#!/usr/bin/env bash
# check-renovacion-licencia-conducir.sh
# Cron mensual día 1 — alerta si licencia vence < 90 días.
# Programar: 0 9 1 * * cd /Users/elias/Documents/Trabajo/skills && bash scripts/check-renovacion-licencia-conducir.sh
set -euo pipefail
SHARE_DIR="${PLUGINS_MX_SHARE_DIR:-$HOME/.local/share/plugins-mx}"
TRACKER="$SHARE_DIR/licencias-conducir.jsonl"
[ ! -f "$TRACKER" ] || ! command -v jq >/dev/null && exit 0
hoy=$(date +%Y-%m-%d)
jq -r --arg h "$hoy" 'select(.vence > $h)' "$TRACKER" | while read -r line; do
    nombre=$(echo "$line" | jq -r '.nombre_hash // "?"')
    vence=$(echo "$line" | jq -r '.vence')
    dias=$(( ($(date -j -f "%Y-%m-%d" "$vence" +%s 2>/dev/null || date -d "$vence" +%s) - $(date +%s)) / 86400 ))
    if [ "$dias" -le 90 ]; then
        echo "⚠ Licencia $nombre vence en $dias días ($vence)"
    fi
done
