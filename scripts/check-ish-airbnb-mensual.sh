#!/usr/bin/env bash
# check-ish-airbnb-mensual.sh
# Día 15 mensual — alerta declaración ISH al fisco estatal (deadline típico 20).
set -euo pipefail
SHARE_DIR="${PLUGINS_MX_SHARE_DIR:-$HOME/.local/share/plugins-mx}"
TRACKER="$SHARE_DIR/airbnb-propiedades.jsonl"
[ -f "$TRACKER" ] || exit 0
hoy=$(date +%Y-%m-%d)
echo "[$hoy] 📅 Alerta ISH mensual — declarar al fisco estatal antes del día 20"
echo "  → Ejecuta /airbnb:fiscal para generar reporte por propiedad"
