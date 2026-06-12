#!/usr/bin/env bash
# PostToolUse: si Edit/Write tocó un archivo en _shared/, sugiere ejecutar sync-shared.sh
# (No lo ejecuta automáticamente — riesgoso. Solo recuerda al usuario.)

set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$SCRIPT_DIR/_lib.sh"

HOOK_NAME="sincronizar-shared-post-edit"
require_jq_or_skip "$HOOK_NAME"

input=$(hook_read_input)

tool_name=$(echo "$input" | jq -r '.tool_name // empty')
case "$tool_name" in
    Edit|Write|MultiEdit) ;;
    *) exit 0 ;;
esac

file_path=$(echo "$input" | jq -r '.tool_input.file_path // .tool_input.path // empty')
case "$file_path" in
    *_shared/*) ;;
    *) exit 0 ;;
esac

emit_info "sincronizar-shared-post-edit: cambios en _shared/. Recordatorio:"
echo "  → ejecuta: bash scripts/sync-shared.sh <vertical>"
echo "  → o: bash scripts/sync-shared.sh --all"
hook_log "$HOOK_NAME" "reminded" "$file_path"
exit 0
