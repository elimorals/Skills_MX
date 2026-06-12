#!/usr/bin/env bash
# imss-pia-mensual.sh
# Cron día 12 de cada mes 09:00: generar PIA (Pago Inicial Ajustado IMSS) para patrones.
set -euo pipefail
REPO="${PATH_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
DATA="$REPO/data/empleados.json"
[ ! -f "$DATA" ] && exit 0

MES=$(date +%Y-%m)
OUT="$REPO/alertas/imss/$MES.md"
mkdir -p "$(dirname "$OUT")"
cat > "$OUT" <<EOF
# 📋 IMSS — Cédula mensual (PIA) periodo $MES

Plazo de pago: día 17 del mes en curso (post-cierre del mes anterior).

Acción:
1. Generar cédula vía mp_imss_patronal.generar_emcr (mock o real con e.firma)
2. Validar nómina del mes anterior contra altas/bajas IDSE
3. Pagar antes del día 17 para evitar recargos del 25% mensual

Empleados activos: $(wc -l < "$DATA")
EOF
echo "$(date -Iseconds) - Alerta IMSS PIA generada"
