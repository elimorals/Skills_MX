#!/usr/bin/env bash
# ultima-alerta-deadline.sh
# Cron día 17 de cada mes 08:00: última alerta deadline pago provisional.
#
# Si el día 16 el usuario no marcó como pagado el provisional, alertar con
# máxima prioridad (sonido + WhatsApp + email).

set -euo pipefail

REPO="${PATH_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
MES=$(date +%Y-%m)
PAGO_FILE="$REPO/fiscal/$MES/pago-provisional.md"
ESTADO_FILE="$REPO/fiscal/$MES/estado-pago.json"

# Si estado-pago.json indica pagado=true, no alertar
if [ -f "$ESTADO_FILE" ] && grep -q '"pagado": *true' "$ESTADO_FILE"; then
  echo "$(date -Iseconds) - Pago provisional ya marcado como pagado. OK."
  exit 0
fi

mkdir -p "$REPO/alertas/$(date +%Y-%m-%d)"
cat > "$REPO/alertas/$(date +%Y-%m-%d)/DEADLINE-HOY-PAGO-PROVISIONAL.md" <<EOF
# 🚨🚨🚨 ÚLTIMA ALERTA — DEADLINE HOY

**Pago provisional $MES vence HOY (día 17)**.

Si no se paga hoy:
- Recargos del 1.47% mensual sobre el adeudo
- Actualización por inflación
- Posibles multas de \$1,400 a \$17,370 MXN
- En reincidencia: clausura

ACCIÓN INMEDIATA:
1. Generar línea de captura en https://www.sat.gob.mx/declaraciones
2. Pagar antes de las 23:59 horas locales
3. Marcar como pagado: \`echo '{"pagado": true, "fecha": "'\$(date -Iseconds)'"}' > $ESTADO_FILE\`

Reporte de cálculo: $PAGO_FILE
EOF

echo "$(date -Iseconds) - ÚLTIMA ALERTA generada"
