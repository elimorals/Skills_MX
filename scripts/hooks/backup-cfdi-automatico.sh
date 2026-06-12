#!/usr/bin/env bash
# PostToolUse: tras timbrar CFDI exitoso, registra el UUID + ruta en backup index.
# (El XML/PDF en sí los guarda el MCP. Este hook indexa metadatos.)

set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$SCRIPT_DIR/_lib.sh"

HOOK_NAME="backup-cfdi-automatico"
require_jq_or_skip "$HOOK_NAME"

input=$(hook_read_input)

tool_name=$(echo "$input" | jq -r '.tool_name // empty')
case "$tool_name" in
    mp_facturama_extendido__timbrar_cfdi) ;;
    *) exit 0 ;;
esac

uuid=$(echo "$input" | jq -r '.tool_result.uuid // .tool_result.UUID // empty')
xml_path=$(echo "$input" | jq -r '.tool_result.xml_path // empty')
pdf_path=$(echo "$input" | jq -r '.tool_result.pdf_path // empty')

if [ -z "$uuid" ] || [ "$uuid" = "null" ]; then
    exit 0
fi

BACKUP_INDEX="$SHARE_DIR/cfdi-backup-index.jsonl"
mkdir -p "$(dirname "$BACKUP_INDEX")"
ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
printf '{"ts":"%s","uuid":"%s","xml":"%s","pdf":"%s"}\n' \
    "$ts" "$uuid" "$xml_path" "$pdf_path" >> "$BACKUP_INDEX"

emit_info "backup-cfdi-automatico: indexado UUID $uuid"
hook_log "$HOOK_NAME" "logged" "uuid=$uuid"
exit 0
