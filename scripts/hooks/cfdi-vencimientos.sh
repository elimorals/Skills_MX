#!/usr/bin/env bash
# SessionStart sub-hook: alerta PPDs sin REP > 30 días.
# Busca $SHARE_DIR/cfdi-ppd-tracker.jsonl con entradas {uuid, fecha_emision, tiene_rep}.

set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$SCRIPT_DIR/_lib.sh"

HOOK_NAME="cfdi-vencimientos"

TRACKER="$SHARE_DIR/cfdi-ppd-tracker.jsonl"

if [ ! -f "$TRACKER" ] || ! command -v jq >/dev/null 2>&1; then
    exit 0
fi

cutoff=$(date -u -v-30d +"%Y-%m-%d" 2>/dev/null || date -u -d "-30 days" +"%Y-%m-%d" 2>/dev/null || echo "")

if [ -z "$cutoff" ]; then
    exit 0
fi

vencidos=$(jq -c "select(.tiene_rep == false and .fecha_emision < \"$cutoff\")" "$TRACKER" 2>/dev/null | head -5)

if [ -z "$vencidos" ]; then
    exit 0
fi

echo ""
echo "⚠ PPDs sin REP > 30 días (top 5):"
echo "$vencidos" | while IFS= read -r line; do
    uuid=$(echo "$line" | jq -r '.uuid // "?"' | head -c 36)
    fecha=$(echo "$line" | jq -r '.fecha_emision // "?"')
    printf "   • %s  emitido %s\n" "$uuid" "$fecha"
done
echo "   → recordatorio: emitir REP o cancelar"

hook_log "$HOOK_NAME" "alerted" ""
exit 0
