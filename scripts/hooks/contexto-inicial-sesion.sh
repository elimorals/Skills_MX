#!/usr/bin/env bash
# SessionStart: orquestador — imprime un dashboard fiscal del día.
# Llama a los 3 hooks de SessionStart en secuencia.

set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$SCRIPT_DIR/_lib.sh"

HOOK_NAME="contexto-inicial-sesion"

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  plugins-mx — contexto inicial $(date '+%Y-%m-%d %H:%M %Z')"
echo "═══════════════════════════════════════════════════════════════"

# Cada sub-hook es opcional. Si falta, sigue.
for sub in alerta-pago-provisional cfdi-vencimientos dashboard-cobranza-pendiente; do
    script="$SCRIPT_DIR/$sub.sh"
    if [ -x "$script" ]; then
        bash "$script" || true
    fi
done

echo "═══════════════════════════════════════════════════════════════"
echo ""

hook_log "$HOOK_NAME" "completed" ""
exit 0
