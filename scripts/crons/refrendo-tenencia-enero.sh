#!/usr/bin/env bash
# refrendo-tenencia-enero.sh
# Cron 2 enero 09:00: alertar refrendo + tenencia + descuentos por pronto pago.
set -euo pipefail
REPO="${PATH_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
MES=$(date +%m)
[ "$MES" != "01" ] && exit 0  # solo en enero

DATA="$REPO/data/autos-usuario.json"
[ ! -f "$DATA" ] && exit 0

OUT="$REPO/alertas/refrendo/$(date +%Y)/aviso-pronto-pago.md"
mkdir -p "$(dirname "$OUT")"
cat > "$OUT" <<EOF
# 💰 Refrendo y tenencia $(date +%Y) — descuentos pronto pago

CDMX típico: descuento del 100% en refrendo si pagas antes del 31 de marzo.
EdoMex típico: descuento del 8% en tenencia si pagas antes del 31 de marzo.

REVISAR: $DATA con todos tus vehículos.

Acción: pagar antes del 31 marzo para máximo ahorro.
EOF
echo "$(date -Iseconds) - Alerta refrendo enero generada"
