#!/usr/bin/env bash
# cobranza-recurrente.sh
# Cron mensual día 1 que arranca la corrida de cobranza recurrente del mes.
#
# Programar (Linux):
#    0 9 1 * * cd /Users/elias/Documents/Trabajo/skills && bash scripts/cobranza-recurrente.sh >> /tmp/plugins-mx-cobranza.log 2>&1
#
# Lee tracker local de clientes recurrentes y genera lista de pagos esperados.
# El envío real lo hace el workflow desde Claude Code — este cron solo prepara.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

ISO_DATE=$(date +%Y-%m-%d)
SHARE_DIR="${PLUGINS_MX_SHARE_DIR:-$HOME/.local/share/plugins-mx}"
TRACKER="$SHARE_DIR/clientes-recurrentes.jsonl"
QUEUE="$SHARE_DIR/cobranza-pendiente.jsonl"

mkdir -p "$SHARE_DIR"

echo "[$(date +%Y-%m-%dT%H:%M:%S)] Arrancando cobranza recurrente del mes"

if [ ! -f "$TRACKER" ]; then
    echo "  ⚠ Tracker $TRACKER no existe — sin clientes recurrentes registrados"
    exit 0
fi

if ! command -v jq >/dev/null 2>&1; then
    echo "  ⚠ jq no instalado — saltando"
    exit 0
fi

# Reset queue del mes
> "$QUEUE"

count=0
while IFS= read -r line; do
    cliente=$(echo "$line" | jq -r '.cliente_hash // .cliente // empty')
    monto=$(echo "$line" | jq -r '.monto_mensual_mxn // 0')
    if [ -z "$cliente" ] || [ "$monto" = "0" ]; then
        continue
    fi
    echo "{\"cliente_hash\":\"$cliente\",\"monto\":$monto,\"dias_vencido\":0,\"fecha_agregado\":\"$ISO_DATE\"}" >> "$QUEUE"
    count=$((count+1))
done < "$TRACKER"

echo "[$(date +%Y-%m-%dT%H:%M:%S)] ✓ $count clientes encolados en $QUEUE"
echo "  → Próximo paso: invocar /freelancers:cobranza-mensual o /core:cobranza desde Claude Code"
