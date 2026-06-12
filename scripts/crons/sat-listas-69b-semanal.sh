#!/usr/bin/env bash
# sat-listas-69b-semanal.sh
# Cron lunes 09:15: validar que cliente/proveedor no entraron a lista 69-B esta semana.
# Complementa el refresh ya existente con notificación por delta.
set -euo pipefail
REPO="${PATH_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
RFCS_DATA="$REPO/data/rfcs-cartera.json"  # clientes + proveedores activos
[ ! -f "$RFCS_DATA" ] && exit 0

OUT_DIR="$REPO/alertas/69b/$(date +%Y-W%V)"
mkdir -p "$OUT_DIR"

echo "$(date -Iseconds) - Validando cartera contra lista 69-B vigente..."
echo "TODO: cruzar $RFCS_DATA contra listas/69b-efos.json + 69-incumplidos.json"
echo "Si hay nuevos en lista: generar alertas para cada RFC + impacto"
echo "$RFCS_DATA" > "$OUT_DIR/manifest-rfcs.txt"
