#!/usr/bin/env bash
# check-wa-pendientes.sh
# Cron cada 30min L-V 9-18: revisar mensajes WhatsApp pendientes de respuesta.
#
# Lee bitácora de mp_meta_whatsapp_cloud y detecta conversaciones del cliente
# sin respuesta del usuario en > 4h dentro de horario laboral.
#
# Genera alerta para que el usuario las atienda.

set -euo pipefail

REPO="${PATH_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
WA_LOG="$REPO/audit-log/meta_whatsapp/$(date +%Y-%m).jsonl"
OUT_DIR="$REPO/alertas/wa/$(date +%Y-%m-%d)"
mkdir -p "$OUT_DIR"

if [ ! -f "$WA_LOG" ]; then
  # Sin actividad WA aún este mes — no hay nada que checar
  exit 0
fi

# Detectar entradas con tipo="mensaje_entrante" sin respuesta correlacionada
# Por ahora: indicar el conteo de entrantes del día sin respuesta del usuario
HOY=$(date +%Y-%m-%d)
ENTRANTES=$(grep -c "\"$HOY" "$WA_LOG" 2>/dev/null || echo "0")

if [ "$ENTRANTES" -gt 0 ]; then
  cat > "$OUT_DIR/pendientes-$(date +%H%M).md" <<EOF
# WhatsApp pendientes — $HOY $(date +%H:%M)

Entradas registradas hoy: $ENTRANTES

Revisar audit-log: $WA_LOG

TODO: análisis fino del JSONL para detectar SOLO los sin respuesta > 4h.
EOF
fi
