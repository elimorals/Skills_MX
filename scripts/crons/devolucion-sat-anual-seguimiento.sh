#!/usr/bin/env bash
# devolucion-sat-anual-seguimiento.sh
# Cron diario L-V 11:00 entre mayo y agosto: seguimiento devolución saldo a favor anual.
set -euo pipefail
MES=$(date +%m)
DIA=$(date +%u)
case "$MES" in 05|06|07|08) ;; *) exit 0 ;; esac
[ "$DIA" -gt 5 ] && exit 0

REPO="${PATH_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
DATA="$REPO/data/devoluciones-sat-curso.json"
[ ! -f "$DATA" ] && exit 0

OUT="$REPO/alertas/devolucion-sat/$(date +%Y-%m-%d).md"
mkdir -p "$(dirname "$OUT")"
cat > "$OUT" <<EOF
# 💰 Seguimiento devolución SAT — $(date +%Y-%m-%d)

Solicitudes en curso: $(cat "$DATA" | python3 -c "import json,sys;print(len(json.load(sys.stdin)))")

Acción:
1. Consultar status de cada solicitud en portal SAT
2. Si requerimiento: responder en plazo (10 días hábiles típico)
3. Si autorizado: confirmar CLABE para depósito
4. Si rechazado: analizar motivo para reactivar o ajustar siguiente
EOF
echo "$(date -Iseconds) - Seguimiento devolución SAT"
