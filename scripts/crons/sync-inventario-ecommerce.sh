#!/usr/bin/env bash
# sync-inventario-ecommerce.sh
# Cron cada 2 horas L-V 9-21: sincronizar inventario entre canales (ML + Shopify + Amazon).
set -euo pipefail
HORA=$(date +%H)
DIA=$(date +%u)
[ "$DIA" -gt 5 ] && exit 0  # solo L-V
[ "$HORA" -lt 9 ] || [ "$HORA" -gt 21 ] && exit 0

REPO="${PATH_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
OUT_DIR="$REPO/sync-multicanal/$(date +%Y-%m-%d-%H)"
mkdir -p "$OUT_DIR"
echo "$(date -Iseconds) - Trigger workflow sync-multicanal (ecommerce-mx)" > "$OUT_DIR/trigger.log"
