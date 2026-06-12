#!/usr/bin/env bash
# cofepris-vencimientos.sh
# Cron primer día de cada trimestre 09:00: revisar vencimientos COFEPRIS.
set -euo pipefail
REPO="${PATH_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
DIA=$(date +%d)
MES=$(date +%m)
[ "$DIA" != "01" ] && exit 0
# Solo enero, abril, julio, octubre
case "$MES" in 01|04|07|10) ;; *) exit 0 ;; esac

DATA="$REPO/data/cofepris-tramites.json"
[ ! -f "$DATA" ] && exit 0

OUT="$REPO/alertas/cofepris/$(date +%Y-Q$(( ($(date +%m)-1)/3 + 1 ))).md"
mkdir -p "$(dirname "$OUT")"
cat > "$OUT" <<EOF
# 🏥 COFEPRIS — revisión trimestral $(date +%Y-Q$(( ($(date +%m)-1)/3 + 1 )))

Documentos a revisar vigencia:
- Aviso de Funcionamiento
- Responsable Sanitario (QFB) cédula
- Licencia Sanitaria
- Convenio disposición RBI
- Programa Garantía Calidad
- PEEC participación trimestral
EOF
echo "$(date -Iseconds) - Revisión trimestral COFEPRIS generada"
