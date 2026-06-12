#!/usr/bin/env bash
# cobranza-renta-mensual.sh
# Cron día 1 de mes 09:30: cobrar rentas + emitir CFDI arrendamiento.
set -euo pipefail
REPO="${PATH_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
DATA="$REPO/data/inmuebles-arrendados.json"
[ ! -f "$DATA" ] && exit 0

MES=$(date +%Y-%m)
OUT_DIR="$REPO/cobranza-renta/$MES"
mkdir -p "$OUT_DIR"
cp "$DATA" "$OUT_DIR/manifest.json"
echo "$(date -Iseconds) - Manifest renta $MES guardado para procesar por workflow cobranza-renta"
