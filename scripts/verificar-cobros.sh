#!/usr/bin/env bash
# verificar-cobros.sh
# Cron mensual día 5 que verifica qué clientes ya pagaron de la cobranza recurrente.
# Cruza tracker de cobranza con tracker de pagos (alimentado por webhooks / banco / manual).
#
# Programar:
#    0 10 5 * * cd /Users/elias/Documents/Trabajo/skills && bash scripts/verificar-cobros.sh >> /tmp/plugins-mx-verificar.log 2>&1

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SHARE_DIR="${PLUGINS_MX_SHARE_DIR:-$HOME/.local/share/plugins-mx}"
QUEUE="$SHARE_DIR/cobranza-pendiente.jsonl"
PAGOS="$SHARE_DIR/pagos-recibidos.jsonl"

echo "[$(date +%Y-%m-%dT%H:%M:%S)] Verificando cobros del mes (D+5)"

if [ ! -f "$QUEUE" ]; then
    echo "  ⚠ Sin queue de cobranza activa"
    exit 0
fi

if ! command -v jq >/dev/null 2>&1; then
    echo "  ⚠ jq no instalado"
    exit 0
fi

pendientes=0
pagados=0
total_pagado_mxn=0

TMP="$(mktemp)"
while IFS= read -r line; do
    cliente=$(echo "$line" | jq -r '.cliente_hash // empty')
    monto=$(echo "$line" | jq -r '.monto // 0')

    pagado=false
    if [ -f "$PAGOS" ]; then
        match=$(jq -r --arg c "$cliente" 'select(.cliente_hash == $c)' "$PAGOS" 2>/dev/null | head -1)
        if [ -n "$match" ]; then
            pagado=true
        fi
    fi

    if [ "$pagado" = "true" ]; then
        pagados=$((pagados+1))
        total_pagado_mxn=$(echo "$total_pagado_mxn + $monto" | bc 2>/dev/null || echo "$total_pagado_mxn")
    else
        # mantener en queue con dias_vencido actualizado
        echo "$line" | jq '.dias_vencido = 5' >> "$TMP"
        pendientes=$((pendientes+1))
    fi
done < "$QUEUE"

mv "$TMP" "$QUEUE"

echo "[$(date +%Y-%m-%dT%H:%M:%S)] ✓ Resultados:"
echo "  • $pagados pagaron (\$$total_pagado_mxn MXN)"
echo "  • $pendientes pendientes (D+5)"
echo "  → Si pendientes > 0: invocar /core:cobranza nivel 2 desde Claude Code"
