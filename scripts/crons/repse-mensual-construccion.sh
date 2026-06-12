#!/usr/bin/env bash
# repse-mensual-construccion.sh
# Cron día 8 de mes 09:00: validar REPSE vigente subcontratistas + cédula informativa SAT.
set -euo pipefail
REPO="${PATH_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
DATA="$REPO/data/subcontratistas-repse.json"
[ ! -f "$DATA" ] && exit 0

MES=$(date +%Y-%m)
OUT="$REPO/alertas/repse/$MES.md"
mkdir -p "$(dirname "$OUT")"
cat > "$OUT" <<EOF
# 🏗 REPSE — verificación mensual subcontratistas

Plazo informativa SAT: día 17 del mes siguiente.

Acciones:
1. Validar status REPSE vigente de cada subcontratista (consultar padrón STPS)
2. Si alguno vencido: gastos NO deducibles + sin acreditamiento de IVA
3. Generar CFDI tipo R retenciones por servicios especializados (6% IVA)
4. Enviar informativa de subcontratación al SAT
EOF
echo "$(date -Iseconds) - Alerta REPSE generada"
