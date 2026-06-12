#!/usr/bin/env bash
# PreToolUse: cuando Write/Edit toca un archivo de "ficha cliente", valida campos mínimos.
# Patron del file_path para activar: */clientes/*.json | */fichas/*.json

set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$SCRIPT_DIR/_lib.sh"

HOOK_NAME="validar-ficha-cliente"
require_jq_or_skip "$HOOK_NAME"

input=$(hook_read_input)

file_path=$(echo "$input" | jq -r '.tool_input.file_path // .tool_input.path // empty')

# Solo aplica a ficha cliente
case "$file_path" in
    */clientes/*.json|*/fichas/*.json) ;;
    *) exit 0 ;;
esac

content=$(echo "$input" | jq -r '.tool_input.content // .tool_input.new_string // empty')
if [ -z "$content" ]; then
    exit 0
fi

# Parse JSON
parsed=$(echo "$content" | jq -e '.' 2>/dev/null) || {
    emit_warning "validar-ficha-cliente: JSON malformado en $file_path"
    hook_log "$HOOK_NAME" "warned" "invalid_json"
    exit 0
}

missing=()
for field in rfc nombre email tel; do
    if [ -z "$(echo "$parsed" | jq -r ".$field // empty")" ]; then
        missing+=("$field")
    fi
done

if [ ${#missing[@]} -gt 0 ]; then
    emit_warning "validar-ficha-cliente: campos faltantes en $file_path: ${missing[*]}"
    hook_log "$HOOK_NAME" "warned" "missing=${missing[*]}"
fi

exit 0
