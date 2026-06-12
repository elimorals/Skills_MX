#!/usr/bin/env bash
# check-wa-pendientes.sh
# Cron cada 30min L-V 9-18 — revisa si hay WhatsApp pendientes de responder.
#
# Programar:
#    */30 9-18 * * 1-5 cd /Users/elias/Documents/Trabajo/skills && bash scripts/check-wa-pendientes.sh >> /tmp/plugins-mx-wa.log 2>&1

set -euo pipefail

SHARE_DIR="${PLUGINS_MX_SHARE_DIR:-$HOME/.local/share/plugins-mx}"
INBOX="$SHARE_DIR/wa-inbox.jsonl"

if [ ! -f "$INBOX" ]; then
    exit 0
fi

if ! command -v jq >/dev/null 2>&1; then
    exit 0
fi

pendientes=$(jq -r 'select(.status == "pending")' "$INBOX" 2>/dev/null | wc -l | tr -d ' ')

if [ "$pendientes" -gt 0 ]; then
    if date -v-30M +%Y-%m-%dT%H:%M >/dev/null 2>&1; then
        cutoff=$(date -v-30M +"%Y-%m-%dT%H:%M")
    else
        cutoff=$(date -d "30 minutes ago" +"%Y-%m-%dT%H:%M")
    fi
    nuevos=$(jq -r --arg c "$cutoff" 'select(.status == "pending" and .ts >= $c)' "$INBOX" 2>/dev/null | wc -l | tr -d ' ')
    if [ "$nuevos" -gt 0 ]; then
        echo "📩 $nuevos WA nuevos sin contestar (total pendientes: $pendientes)"
        echo "  → ejecuta /core:wa-procesar para procesarlos"
    fi
fi
