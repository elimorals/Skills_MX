#!/usr/bin/env bash
# comisiones-medicos-mensual.sh
# Cron día 3 de mes 10:00: calcular y emitir comisiones a médicos referentes del laboratorio.
set -euo pipefail
REPO="${PATH_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
DATA="$REPO/data/medicos-referentes-lab.json"
[ ! -f "$DATA" ] && exit 0

MES=$(date -v-1m +%Y-%m 2>/dev/null || date -d "$(date +%Y-%m-01) -1 day" +%Y-%m)
OUT="$REPO/comisiones-lab/$MES/calculo.md"
mkdir -p "$(dirname "$OUT")"
cat > "$OUT" <<EOF
# 💊 Comisiones médicos referentes — $MES

Acción:
1. Consolidar pacientes referidos por médico (mes anterior)
2. Calcular ingreso del lab por cada uno
3. Aplicar % comisión acordado por médico
4. Generar CFDI pro-forma para que médico timbre (régimen 612 típico)
5. Aplicar retenciones 10% ISR + 10.67% IVA (lab retiene como PM)
6. Dispersar via SPEI a cada médico
EOF
echo "$(date -Iseconds) - Cálculo comisiones lab generado"
