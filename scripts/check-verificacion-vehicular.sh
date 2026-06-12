#!/usr/bin/env bash
# check-verificacion-vehicular.sh
# Diario 08:00 — alerta si vehículo entra en periodo de verificación próximo.
set -euo pipefail
SHARE_DIR="${PLUGINS_MX_SHARE_DIR:-$HOME/.local/share/plugins-mx}"
TRACKER="$SHARE_DIR/placas-vehiculos.jsonl"
[ -f "$TRACKER" ] || exit 0
hoy=$(date +%Y-%m-%d)
mes=$(date +%m)
echo "[$hoy] Check verificación vehicular"
# (lógica simplificada — alerta por ahora si hay placas registradas)
count=$(wc -l < "$TRACKER" | tr -d ' ')
echo "  → $count vehículos registrados — revisar verificaciones próximas con /vehiculos:verificar"
