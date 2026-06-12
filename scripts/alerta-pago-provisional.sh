#!/usr/bin/env bash
# alerta-pago-provisional.sh
# Cron mensual día 15 — alerta de pago provisional ISR/IVA (vence día 17).
#
# Programar:
#    0 10 15 * * cd /Users/elias/Documents/Trabajo/skills && bash scripts/alerta-pago-provisional.sh >> /tmp/plugins-mx-alerta-prov.log 2>&1

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SHARE_DIR="${PLUGINS_MX_SHARE_DIR:-$HOME/.local/share/plugins-mx}"
NOTIFICATION="$SHARE_DIR/notifications.jsonl"

mkdir -p "$SHARE_DIR"
ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

if date -v-1m +%B >/dev/null 2>&1; then
    MES_OBLIG=$(date -v-1m +%B)
else
    MES_OBLIG=$(date -d "1 month ago" +%B)
fi

echo "[$(date +%Y-%m-%dT%H:%M:%S)] 🚨 ALERTA: Pago provisional ISR/IVA"
echo "  • Mes a pagar: $MES_OBLIG"
echo "  • Deadline SAT: día 17 del mes en curso"
echo "  • Faltan: ~2 días hábiles"
echo "  • Acción: ejecutar /core:cierre-fiscal-mensual y presentar en línea"
echo ""

echo "{\"ts\":\"$ts\",\"tipo\":\"pago_provisional\",\"mes_obligacion\":\"$MES_OBLIG\",\"deadline_dia\":17,\"urgencia\":\"alta\"}" >> "$NOTIFICATION"

echo "  → Notificación persistida en $NOTIFICATION"
