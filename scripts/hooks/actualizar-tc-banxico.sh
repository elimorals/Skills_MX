#!/usr/bin/env bash
# PostToolUse: tras consultar Banxico, marca cache como fresco (timestamp).
# El cache real lo maneja el MCP; este hook solo marca "última actualización".

set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$SCRIPT_DIR/_lib.sh"

HOOK_NAME="actualizar-tc-banxico"
require_jq_or_skip "$HOOK_NAME"

input=$(hook_read_input)

tool_name=$(echo "$input" | jq -r '.tool_name // empty')
case "$tool_name" in
    mp_banxico__*) ;;
    *) exit 0 ;;
esac

ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo "$ts" > "$CACHE_DIR/banxico-last-refresh.txt" 2>/dev/null

hook_log "$HOOK_NAME" "refreshed" "tool=$tool_name"
exit 0
