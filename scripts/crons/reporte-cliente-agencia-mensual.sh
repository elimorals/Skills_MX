#!/usr/bin/env bash
# reporte-cliente-agencia-mensual.sh
# Cron día 2 de mes 09:00: trigger generación reportes mensuales de agencia a cada cliente.
set -euo pipefail
REPO="${PATH_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
DATA="$REPO/data/clientes-agencia.json"
[ ! -f "$DATA" ] && exit 0

MES=$(date -v-1m +%Y-%m 2>/dev/null || date -d "$(date +%Y-%m-01) -1 day" +%Y-%m)
OUT_DIR="$REPO/reportes-agencia/$MES"
mkdir -p "$OUT_DIR"
cp "$DATA" "$OUT_DIR/manifest.json"
echo "$(date -Iseconds) - Manifest reportes $MES guardado para procesar por skill reporte-mensual-cliente"
