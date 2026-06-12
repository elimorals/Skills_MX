#!/usr/bin/env bash
# Stop: cleanup al cerrar sesión.
# - Compacta logs > 100MB
# - Backup ligero de bitácora

set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$SCRIPT_DIR/_lib.sh"

HOOK_NAME="cleanup-sesion"

# Compacta hook log si es grande
if [ -f "$HOOK_LOG" ]; then
    size=$(wc -c < "$HOOK_LOG" 2>/dev/null || echo 0)
    if [ "$size" -gt 104857600 ]; then  # 100MB
        # Mantener solo últimas 10k líneas
        tail -10000 "$HOOK_LOG" > "$HOOK_LOG.tmp" && mv "$HOOK_LOG.tmp" "$HOOK_LOG"
        hook_log "$HOOK_NAME" "compacted" "size_before=$size"
    fi
fi

hook_log "$HOOK_NAME" "completed" ""
exit 0
