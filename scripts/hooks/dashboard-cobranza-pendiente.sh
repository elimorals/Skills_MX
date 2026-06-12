#!/usr/bin/env bash
# SessionStart sub-hook: muestra cartera vencida si existe un tracker local.
# Buscamos $SHARE_DIR/cobranza-pendiente.jsonl con entradas {cliente,monto,dias_vencido}.

set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$SCRIPT_DIR/_lib.sh"

HOOK_NAME="dashboard-cobranza-pendiente"

TRACKER="$SHARE_DIR/cobranza-pendiente.jsonl"

if [ ! -f "$TRACKER" ]; then
    exit 0
fi

if ! command -v jq >/dev/null 2>&1; then
    exit 0
fi

vencidos=$(jq -c 'select(.dias_vencido > 0)' "$TRACKER" 2>/dev/null | head -5)

if [ -z "$vencidos" ]; then
    exit 0
fi

echo ""
echo "💰 Cobranza pendiente (top 5):"
echo "$vencidos" | while IFS= read -r line; do
    cliente=$(echo "$line" | jq -r '.cliente_hash // .cliente // "?"' | head -c 12)
    monto=$(echo "$line" | jq -r '.monto // 0')
    dias=$(echo "$line" | jq -r '.dias_vencido // 0')
    printf "   • %-12s  \$%-12s  %s días\n" "$cliente" "$monto" "$dias"
done

hook_log "$HOOK_NAME" "shown" ""
exit 0
