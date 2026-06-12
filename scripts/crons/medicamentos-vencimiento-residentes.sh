#!/usr/bin/env bash
# medicamentos-vencimiento-residentes.sh
# Cron diario 07:30: revisar medicamentos por vencer/agotarse de residentes geriátricos.
set -euo pipefail
REPO="${PATH_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
DATA="$REPO/data/medicamentos-residentes.json"
[ ! -f "$DATA" ] && exit 0

OUT_DIR="$REPO/alertas/medicamentos/$(date +%Y-%m-%d)"
mkdir -p "$OUT_DIR"

python3 - <<'PYEOF' "$DATA" "$OUT_DIR"
import json, sys
from datetime import datetime
data = json.load(open(sys.argv[1]))
hoy = datetime.now().date()
agotandose = []
vencidos = []
for med in data:
    if med.get("dias_para_agotarse", 999) <= 14:
        agotandose.append(med)
    venc_str = med.get("caducidad_lote")
    if venc_str:
        venc = datetime.fromisoformat(venc_str).date()
        if (venc - hoy).days <= 30:
            vencidos.append(med)
if agotandose:
    json.dump(agotandose, open(f"{sys.argv[2]}/por-agotarse.json", "w"), indent=2, ensure_ascii=False)
    print(f"⚠ {len(agotandose)} medicamentos próximos a agotarse")
if vencidos:
    json.dump(vencidos, open(f"{sys.argv[2]}/por-vencer.json", "w"), indent=2, ensure_ascii=False)
    print(f"⚠ {len(vencidos)} medicamentos próximos a vencer")
PYEOF
