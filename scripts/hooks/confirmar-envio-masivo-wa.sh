#!/usr/bin/env bash
# PreToolUse: pide confirmación si batch WhatsApp > umbral.
# Si destinatarios > 50, NO bloquea pero deja log de warning explícito.
# (Confirmación interactiva real requiere Claude Code session input — no bash.)

set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$SCRIPT_DIR/_lib.sh"

HOOK_NAME="confirmar-envio-masivo-wa"
require_jq_or_skip "$HOOK_NAME"

UMBRAL="${PLUGINS_MX_WA_BATCH_UMBRAL:-50}"

input=$(hook_read_input)

# Detecta varias formas comunes de pasar el batch
count=$(echo "$input" | jq -r '
    (.tool_input.destinatarios | length) // empty
    // (.tool_input.recipients | length) // empty
    // (.tool_input.batch | length) // empty
    // (.tool_input.numbers | length) // empty
    // 0
')

if [ -z "$count" ] || [ "$count" = "null" ]; then
    count=0
fi

if [ "$count" -gt "$UMBRAL" ]; then
    emit_warning "confirmar-envio-masivo-wa: $count destinatarios > umbral $UMBRAL"
    echo "" >&2
    echo "  → REVISA antes de confirmar:" >&2
    echo "    - ¿La plantilla está aprobada por Meta?" >&2
    echo "    - ¿Tienes opt-in vigente de cada destinatario? (LFPDPPP)" >&2
    echo "    - ¿La frecuencia respeta política Meta (1 marketing/24h)?" >&2
    echo "" >&2
    hook_log "$HOOK_NAME" "warned" "count=$count umbral=$UMBRAL"
fi

exit 0
