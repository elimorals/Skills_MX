#!/usr/bin/env bash
# ish-mensual-airbnb-host.sh
# Cron día 10 de cada mes 09:00: calcular y alertar pago ISH (Impuesto Sobre Hospedaje).
# Aplica a anfitriones Airbnb/Booking. Cada estado varía (CDMX 3.5%, Quintana Roo 3%, etc.).
set -euo pipefail
REPO="${PATH_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
MES_ANTERIOR=$(date -v-1m +%Y-%m 2>/dev/null || date -d "$(date +%Y-%m-01) -1 day" +%Y-%m)
DATA="$REPO/data/airbnb-host.json"
[ ! -f "$DATA" ] && exit 0

OUT="$REPO/alertas/ish/$MES_ANTERIOR.md"
mkdir -p "$(dirname "$OUT")"
cat > "$OUT" <<EOF
# 🏨 ISH (Impuesto sobre Hospedaje) — periodo $MES_ANTERIOR

Recordatorio: declarar y pagar el ISH del mes $MES_ANTERIOR antes del día 17 del mes en curso.

Tasas por estado (validar vigencia):
- CDMX: 3.5%
- Quintana Roo: 3%
- Yucatán: 3%
- Jalisco: 3%
- Nayarit: 2.5%

Acción: usar skill calculador-ish-por-estado para calcular monto y generar línea de captura.
EOF
echo "$(date -Iseconds) - Alerta ISH generada"
