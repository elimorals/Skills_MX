#!/usr/bin/env bash
# PreToolUse genérico: validación estructural mínima de cualquier payload CFDI
# (sea timbrado, validar, generar borrador, etc.).
# Más laxo que pre-timbrado-validation: solo bloquea si JSON está roto.

set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$SCRIPT_DIR/_lib.sh"

HOOK_NAME="validar-cfdi-payload"
require_jq_or_skip "$HOOK_NAME"

input=$(hook_read_input)

# Verifica que tool_input parsea
if ! echo "$input" | jq -e '.tool_input' >/dev/null 2>&1; then
    emit_error "validar-cfdi-payload: tool_input vacío o JSON roto"
    hook_log "$HOOK_NAME" "blocked" "tool_input_invalid"
    exit 2
fi

hook_log "$HOOK_NAME" "passed" ""
exit 0
