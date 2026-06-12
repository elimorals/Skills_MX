#!/usr/bin/env bash
# PreToolUse: log estructurado de cada llamada a tool MCP de plugins-mx.
# Útil para auditoría y debug. Hashea identifiers sensibles (RFC, email, etc.).

set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$SCRIPT_DIR/_lib.sh"

HOOK_NAME="bitacora-mcp-calls"
require_jq_or_skip "$HOOK_NAME"

input=$(hook_read_input)

tool_name=$(echo "$input" | jq -r '.tool_name // empty')

# Solo registra tools de plugins-mx (mp_*)
case "$tool_name" in
    mp_*) ;;
    *) exit 0 ;;
esac

# Hashea campos sensibles
hash_field() {
    if [ -n "$1" ] && [ "$1" != "null" ]; then
        echo -n "$1" | shasum | cut -c1-12
    else
        echo ""
    fi
}

rfc_hash=$(hash_field "$(echo "$input" | jq -r '.tool_input.rfc // .tool_input.rfc_receptor // .tool_input.rfc_emisor // empty')")
email_hash=$(hash_field "$(echo "$input" | jq -r '.tool_input.email // empty')")

BITACORA="$SHARE_DIR/hooks/bitacora-mcp.jsonl"
mkdir -p "$(dirname "$BITACORA")" 2>/dev/null
ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
printf '{"ts":"%s","tool":"%s","rfc_hash":"%s","email_hash":"%s"}\n' \
    "$ts" "$tool_name" "$rfc_hash" "$email_hash" >> "$BITACORA"

hook_log "$HOOK_NAME" "logged" "tool=$tool_name"
exit 0
