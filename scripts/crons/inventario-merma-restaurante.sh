#!/usr/bin/env bash
# inventario-merma-restaurante.sh
# Cron lunes y viernes 22:00: calcular inventario teórico vs físico + merma.
set -euo pipefail
DIA=$(date +%u)  # 1=lunes, 5=viernes
case "$DIA" in 1|5) ;; *) exit 0 ;; esac

REPO="${PATH_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
DATA="$REPO/data/inventario-restaurante.json"
[ ! -f "$DATA" ] && exit 0

OUT="$REPO/alertas/merma/$(date +%Y-%m-%d).md"
mkdir -p "$(dirname "$OUT")"
cat > "$OUT" <<EOF
# 🍽 Inventario y merma — $(date +%Y-%m-%d)

Acción:
1. Conteo físico de cocina (5-10 productos clave)
2. Comparar contra teórico del POS (Soft Restaurant u otro)
3. Calcular merma % vs ventas
4. Si merma > 5% en alguna categoría: alerta + investigar
EOF
echo "$(date -Iseconds) - Reporte inventario/merma generado"
