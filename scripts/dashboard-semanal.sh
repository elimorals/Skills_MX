#!/usr/bin/env bash
# dashboard-semanal.sh
# Cron semanal lunes 09:00 — genera reporte de la semana anterior.
# Cuenta CFDIs emitidos, pagos recibidos, cancelaciones, alertas pendientes.
#
# Programar:
#    0 9 * * 1 cd /Users/elias/Documents/Trabajo/skills && bash scripts/dashboard-semanal.sh >> /tmp/plugins-mx-dashboard.log 2>&1

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SHARE_DIR="${PLUGINS_MX_SHARE_DIR:-$HOME/.local/share/plugins-mx}"

if date -v-7d +%Y-%m-%d >/dev/null 2>&1; then
    DESDE=$(date -v-7d +%Y-%m-%d)
else
    DESDE=$(date -d "7 days ago" +%Y-%m-%d)
fi
HASTA=$(date +%Y-%m-%d)

echo "═══════════════════════════════════════════════════════════════"
echo "  Dashboard semanal — $DESDE al $HASTA"
echo "═══════════════════════════════════════════════════════════════"

# CFDIs
CFDI_BACKUP="$SHARE_DIR/cfdi-backup-index.jsonl"
if [ -f "$CFDI_BACKUP" ] && command -v jq >/dev/null; then
    cfdis_semana=$(jq -r --arg d "$DESDE" --arg h "$HASTA" 'select(.ts >= $d and .ts <= $h)' "$CFDI_BACKUP" 2>/dev/null | wc -l | tr -d ' ')
    echo "📄 CFDIs emitidos: $cfdis_semana"
fi

# Cancelaciones
CANCEL_LOG="$SHARE_DIR/cfdi-cancelaciones.jsonl"
if [ -f "$CANCEL_LOG" ] && command -v jq >/dev/null; then
    cancel_semana=$(jq -r --arg d "$DESDE" --arg h "$HASTA" 'select(.ts >= $d and .ts <= $h)' "$CANCEL_LOG" 2>/dev/null | wc -l | tr -d ' ')
    if [ "$cancel_semana" -gt 0 ]; then
        echo "🗑  Cancelaciones: $cancel_semana"
    fi
fi

# Cobranza pendiente
COBRANZA="$SHARE_DIR/cobranza-pendiente.jsonl"
if [ -f "$COBRANZA" ] && command -v jq >/dev/null; then
    pendientes=$(wc -l < "$COBRANZA" | tr -d ' ')
    vencidos=$(jq -r 'select(.dias_vencido > 0)' "$COBRANZA" 2>/dev/null | wc -l | tr -d ' ')
    echo "💰 Cobranza pendiente: $pendientes (vencidos: $vencidos)"
fi

# Hook events
HOOK_LOG="$SHARE_DIR/hooks/hook-events.jsonl"
if [ -f "$HOOK_LOG" ] && command -v jq >/dev/null; then
    bloqueados=$(jq -r --arg d "$DESDE" 'select(.outcome == "blocked" and .ts >= $d)' "$HOOK_LOG" 2>/dev/null | wc -l | tr -d ' ')
    if [ "$bloqueados" -gt 0 ]; then
        echo "🛡  Hooks bloquearon: $bloqueados acciones"
    fi
fi

echo "═══════════════════════════════════════════════════════════════"
