#!/usr/bin/env bash
# ultima-alerta-deadline.sh
# Cron mensual día 17 — última alerta (deadline pago provisional HOY).
#
# Programar:
#    0 8 17 * * cd /Users/elias/Documents/Trabajo/skills && bash scripts/ultima-alerta-deadline.sh >> /tmp/plugins-mx-deadline.log 2>&1

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SHARE_DIR="${PLUGINS_MX_SHARE_DIR:-$HOME/.local/share/plugins-mx}"
NOTIFICATION="$SHARE_DIR/notifications.jsonl"

mkdir -p "$SHARE_DIR"
ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "[$(date +%Y-%m-%dT%H:%M:%S)] 🚨🚨 HOY VENCE pago provisional ISR/IVA"
echo "  ⚠ Día 17 — si no presentas hoy, recargos + actualización desde mañana"
echo "  → Ejecuta INMEDIATAMENTE: /core:cierre-fiscal-mensual"
echo ""

echo "{\"ts\":\"$ts\",\"tipo\":\"deadline_pago_provisional\",\"urgencia\":\"CRITICA\",\"vence\":\"hoy\"}" >> "$NOTIFICATION"
