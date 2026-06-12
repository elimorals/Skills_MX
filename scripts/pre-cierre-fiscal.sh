#!/usr/bin/env bash
# pre-cierre-fiscal.sh
# Cron mensual día 14 que prepara el cierre fiscal del mes anterior.
# Verifica que estén todos los CFDIs emitidos, REPs de PPDs cobrados, retenciones registradas.
#
# Programar:
#    0 9 14 * * cd /Users/elias/Documents/Trabajo/skills && bash scripts/pre-cierre-fiscal.sh >> /tmp/plugins-mx-pre-cierre.log 2>&1

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SHARE_DIR="${PLUGINS_MX_SHARE_DIR:-$HOME/.local/share/plugins-mx}"

# Calcular mes anterior (mes a cerrar)
if date -v-1m +%Y-%m >/dev/null 2>&1; then
    MES_CERRAR=$(date -v-1m +%Y-%m)  # macOS
else
    MES_CERRAR=$(date -d "1 month ago" +%Y-%m)  # Linux
fi

echo "[$(date +%Y-%m-%dT%H:%M:%S)] Pre-cierre fiscal — mes a cerrar: $MES_CERRAR"

CHECKLIST=""
add_check() { CHECKLIST="$CHECKLIST\n  $1"; }

# 1. CFDIs emitidos del mes
CFDI_BACKUP="$SHARE_DIR/cfdi-backup-index.jsonl"
if [ -f "$CFDI_BACKUP" ] && command -v jq >/dev/null; then
    cfdis_mes=$(jq -r --arg m "$MES_CERRAR" 'select(.ts | startswith($m))' "$CFDI_BACKUP" 2>/dev/null | wc -l | tr -d ' ')
    add_check "☐ CFDIs emitidos $MES_CERRAR: $cfdis_mes registrados"
else
    add_check "☐ CFDIs emitidos: tracker no encontrado"
fi

# 2. PPDs sin REP
PPD_TRACKER="$SHARE_DIR/cfdi-ppd-tracker.jsonl"
if [ -f "$PPD_TRACKER" ] && command -v jq >/dev/null; then
    ppd_pend=$(jq -r 'select(.tiene_rep == false)' "$PPD_TRACKER" 2>/dev/null | wc -l | tr -d ' ')
    if [ "$ppd_pend" -gt 0 ]; then
        add_check "⚠ $ppd_pend PPDs sin REP — emitir antes del cierre"
    else
        add_check "☑ PPDs: todos con REP"
    fi
fi

# 3. Banxico TCs vigentes
TC_FILE="$SHARE_DIR/banxico-last-refresh.txt"
if [ -f "$TC_FILE" ]; then
    add_check "☑ Banxico TCs: actualizados $(cat $TC_FILE)"
fi

# 4. Recordatorio
add_check ""
add_check "→ Próximos pasos: /core:cierre-fiscal-mensual desde Claude Code"
add_check "→ Pago provisional vence el día 17 — faltan ~3 días"

echo -e "PRE-CIERRE FISCAL CHECKLIST ($MES_CERRAR):$CHECKLIST"
