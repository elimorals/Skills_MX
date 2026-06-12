#!/usr/bin/env bash
# cierre-fiscal-anual-marzo.sh
# Cron 1 marzo 09:00: alertar inicio temporada anual + acción.
set -euo pipefail
MES=$(date +%m)
[ "$MES" != "03" ] && exit 0

REPO="${PATH_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
ANIO_DECLARACION=$(($(date +%Y) - 1))
OUT="$REPO/alertas/anual/$(date +%Y)-aviso-inicio.md"
mkdir -p "$(dirname "$OUT")"
cat > "$OUT" <<EOF
# 📅 Temporada anual $ANIO_DECLARACION — inicia hoy

Deadline PF: 30 abril $(date +%Y).

Acción inmediata:
1. Validar e.firma vigente (cron efirma-vencimiento-90d ya alertó si menos de 90d)
2. Correr workflow pf-anual-completa.workflow.js
3. Enviar PDF a contador certificado
4. Presentar antes del 25 abril (margen seguridad)
EOF
echo "$(date -Iseconds) - Aviso anual marzo generado"
