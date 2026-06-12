#!/usr/bin/env bash
# verificar-cobros.sh
# Cron día 5 de cada mes 10:00: verificar qué CFDIs emitidos el día 1 ya fueron cobrados.
#
# Para los CFDIs en cobranza/<mes>/dia-1-emisiones/:
# - Si están como "cobrado" en cfdi/.../<uuid>.json → OK
# - Si no → flaggar para cobranza-multinivel etapa 1

set -euo pipefail

REPO="${PATH_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
MES=$(date +%Y-%m)
COBRANZA_DIR="$REPO/cobranza/$MES"
MANIFEST="$COBRANZA_DIR/dia-1-emisiones/manifest.json"

if [ ! -f "$MANIFEST" ]; then
  echo "$(date -Iseconds) - SKIP: $MANIFEST no existe (no se emitió día 1 este mes)"
  exit 0
fi

OUT_DIR="$COBRANZA_DIR/dia-5-verificacion"
mkdir -p "$OUT_DIR"

echo "$(date -Iseconds) - Verificando cobros del mes $MES..."

# Esta sección hará: para cada UUID, leer cfdi/.../<uuid>.json y checar status
# y construir lista de no_cobrados.json + cobrados.json
echo "TODO: integrar con persistencia de CFDIs cuando esté disponible"
echo "Manifest base: $MANIFEST" > "$OUT_DIR/log.txt"
date -Iseconds >> "$OUT_DIR/log.txt"
