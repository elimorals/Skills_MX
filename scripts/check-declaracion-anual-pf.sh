#!/usr/bin/env bash
# check-declaracion-anual-pf.sh
# Mensual día 1 enero-abril — alerta declaración anual PF (deadline 30 abril).
set -euo pipefail
mes=$(date +%m)
case "$mes" in
    01|02|03) echo "📅 Declaración Anual PF — deadline 30 abril. Iniciar recopilación CFDIs." ;;
    04) echo "🚨 ÚLTIMO MES — declaración anual PF vence 30 abril. Acelerar." ;;
esac
