#!/usr/bin/env bash
# check-refrendo-enero.sh
# Solo enero día 1 — recordatorio refrendo + tenencia (deadline 31 marzo).
set -euo pipefail
mes=$(date +%m)
[ "$mes" = "01" ] || exit 0
echo "📅 ALERTA REFRENDO + TENENCIA ${YEAR:-$(date +%Y)}"
echo "  • Deadline: 31 marzo"
echo "  • Ejecuta /vehiculos:refrendo para calcular monto por placa"
