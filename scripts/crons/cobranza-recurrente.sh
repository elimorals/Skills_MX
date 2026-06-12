#!/usr/bin/env bash
# cobranza-recurrente.sh
# Cron día 1 de cada mes 09:00: emitir CFDIs recurrentes + enviar links de cobro.
#
# Lee $PATH_REPO/data/clientes-recurrentes.json con clientes que tienen iguala/suscripción.
# Para cada uno: genera CFDI del mes + envía WhatsApp con link de pago.

set -euo pipefail

REPO="${PATH_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
DATA_FILE="$REPO/data/clientes-recurrentes.json"
LOG_DIR="${LOG_DIR:-/tmp}"

if [ ! -f "$DATA_FILE" ]; then
  echo "$(date -Iseconds) - SKIP: $DATA_FILE no existe (sin clientes recurrentes)"
  exit 0
fi

OUT_DIR="$REPO/cobranza/$(date +%Y-%m)/dia-1-emisiones"
mkdir -p "$OUT_DIR"

# Listar count de clientes recurrentes
COUNT=$(grep -c '"rfc"' "$DATA_FILE" || echo "0")

echo "$(date -Iseconds) - Procesando $COUNT clientes recurrentes..."
echo "TODO: integrar con workflow cierre-fiscal-mensual + cfdi-emision-completa"
echo "$(date -Iseconds) - Manifest a procesar guardado en $OUT_DIR/manifest.json"
cp "$DATA_FILE" "$OUT_DIR/manifest.json"

# Cuando los workflows estén deployados con un runtime accesible desde cron,
# este script invocará: Workflow({scriptPath: ".../cfdi-emision-completa.workflow.js", args: {...}})
# por cada cliente del manifest.
