#!/usr/bin/env bash
# PostToolUse: si > N cancelaciones de CFDI en últimas 24h, alerta (riesgo SAT detecta operación irregular).

set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$SCRIPT_DIR/_lib.sh"

HOOK_NAME="alert-cancelaciones-frecuentes"
require_jq_or_skip "$HOOK_NAME"

UMBRAL="${PLUGINS_MX_CANCEL_UMBRAL:-3}"

input=$(hook_read_input)

tool_name=$(echo "$input" | jq -r '.tool_name // empty')
case "$tool_name" in
    mp_facturama_extendido__cancelar_cfdi) ;;
    *) exit 0 ;;
esac

CANCEL_LOG="$SHARE_DIR/cfdi-cancelaciones.jsonl"
mkdir -p "$(dirname "$CANCEL_LOG")"
ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
uuid=$(echo "$input" | jq -r '.tool_input.uuid // empty')
echo "{\"ts\":\"$ts\",\"uuid\":\"$uuid\"}" >> "$CANCEL_LOG"

# Cuenta cancelaciones últimas 24h
cutoff_iso=$(date -u -v-24H +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date -u -d "-24 hours" +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || echo "")
count=0
if [ -n "$cutoff_iso" ]; then
    count=$(awk -v cutoff="$cutoff_iso" '$0 ~ /"ts":/ {
        if (match($0, /"ts":"[^"]+"/)) {
            ts = substr($0, RSTART+6, RLENGTH-7)
            if (ts >= cutoff) c++
        }
    } END { print c+0 }' "$CANCEL_LOG")
fi

if [ "$count" -gt "$UMBRAL" ]; then
    emit_warning "alert-cancelaciones-frecuentes: $count cancelaciones en 24h (umbral $UMBRAL) — revisa operación"
    hook_log "$HOOK_NAME" "alerted" "count=$count"
fi

exit 0
