#!/usr/bin/env bash
# templates-wa-status-meta.sh
# Cron diario 10:00: verificar status de templates WhatsApp aprobables (Meta puede recategorizar).
set -euo pipefail
REPO="${PATH_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
DATA="$REPO/data/wa-templates-status.json"
[ ! -f "$DATA" ] && exit 0

OUT="$REPO/alertas/wa-templates/$(date +%Y-%m-%d).md"
mkdir -p "$(dirname "$OUT")"
cat > "$OUT" <<EOF
# 📱 WhatsApp templates — verificación diaria

Plantillas a revisar status Meta:
- APPROVED → todo bien
- PENDING → no usar aún
- REJECTED → revisar motivo y resubmit
- PAUSED → mala tasa entrega, requerir ajuste
- DISABLED → eliminada por violación

Acción si hay cambio: actualizar config local + notificar al manager.
EOF
echo "$(date -Iseconds) - Verificación WA templates"
