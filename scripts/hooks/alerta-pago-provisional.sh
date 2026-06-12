#!/usr/bin/env bash
# SessionStart sub-hook: si hoy es día 14-17 del mes, recuerda pago provisional ISR/IVA.

set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$SCRIPT_DIR/_lib.sh"

HOOK_NAME="alerta-pago-provisional"

dia=$(date '+%d' | sed 's/^0//')

if [ "$dia" -ge 14 ] && [ "$dia" -le 17 ]; then
    diferencia=$((17 - dia))
    if [ "$diferencia" -eq 0 ]; then
        echo ""
        echo "🚨 HOY VENCE pago provisional ISR/IVA del mes anterior"
    elif [ "$diferencia" -gt 0 ]; then
        echo ""
        echo "📅 Faltan $diferencia día(s) para pago provisional ISR/IVA"
    fi
    echo "   Ejecuta: /core:cierre-fiscal-mensual"
    hook_log "$HOOK_NAME" "alerted" "dia=$dia"
fi

exit 0
