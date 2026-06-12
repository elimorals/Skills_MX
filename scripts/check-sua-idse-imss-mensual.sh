#!/usr/bin/env bash
# check-sua-idse-imss-mensual.sh
# Mensual día 17 — alerta presentación SUA-IDSE IMSS patronal.
set -euo pipefail
SHARE_DIR="${PLUGINS_MX_SHARE_DIR:-$HOME/.local/share/plugins-mx}"
TRACKER="$SHARE_DIR/empleados-patronal.jsonl"
[ -f "$TRACKER" ] || exit 0
echo "[$(date +%Y-%m-%d)] 📅 SUA-IDSE IMSS: presentar movimientos del mes anterior"
echo "  → Deadline día 17 mes en curso"
echo "  → /nomina:sua-export para generar archivo"
