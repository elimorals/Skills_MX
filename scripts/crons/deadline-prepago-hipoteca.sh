#!/usr/bin/env bash
# deadline-prepago-hipoteca.sh
# Cron 1 noviembre 09:00: alertar deadline para pre-pago hipotecario aprovechable este ejercicio.
# Diciembre suele tener mejor TC del año + posible aguinaldo + bono → momento ideal pre-pago.
set -euo pipefail
REPO="${PATH_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
MES=$(date +%m)
[ "$MES" != "11" ] && exit 0

DATA="$REPO/data/creditos-hipotecarios.json"
[ ! -f "$DATA" ] && exit 0

OUT="$REPO/alertas/prepago-hipoteca/aviso-diciembre.md"
mkdir -p "$(dirname "$OUT")"
cat > "$OUT" <<EOF
# 🏠 Pre-pago hipotecario diciembre

Momento óptimo para pre-pago si recibes aguinaldo/bono.

Ventajas pre-pago diciembre:
- Aplicas a capital ANTES de cálculo de interés enero (siguiente periodo)
- Aprovechas liquidez del aguinaldo
- Ahorras intereses futuros (modalidad reducción plazo)

Acción: usar skill simulador-prepagos-hipotecarios para evaluar impacto antes del 31 diciembre.
EOF
echo "$(date -Iseconds) - Alerta pre-pago hipoteca generada"
