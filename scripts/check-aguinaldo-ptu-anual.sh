#!/usr/bin/env bash
# check-aguinaldo-ptu-anual.sh
# Anual noviembre — alerta deadlines aguinaldo (20 dic) + PTU (60d post anual fiscal).
set -euo pipefail
mes=$(date +%m)
case "$mes" in
    11) echo "📅 Aguinaldo deadline 20 diciembre — preparar cálculo (15 días mínimo Art. 87 LFT)" ;;
    04|05) echo "📅 PTU deadline: dentro de 60 días después de presentar declaración anual PM" ;;
esac
