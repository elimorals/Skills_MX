#!/usr/bin/env bash
# check-declaracion-donataria-mayo.sh
# Anual abril-mayo — alerta declaración transparencia donataria (deadline 31 mayo).
set -euo pipefail
mes=$(date +%m)
case "$mes" in
    04) echo "📅 Donataria: declaración transparencia vence 31 mayo. Empezar." ;;
    05) echo "🚨 Donataria: declaración transparencia vence 31 mayo. URGENTE." ;;
esac
