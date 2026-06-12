#!/usr/bin/env bash
# polizas-seguros-renovacion-90d.sh
# Cron diario 09:00: revisar pólizas a renovar en próximos 90 días.
set -euo pipefail
REPO="${PATH_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
DATA="$REPO/data/polizas-agente.json"
[ ! -f "$DATA" ] && exit 0

OUT_DIR="$REPO/alertas/polizas/$(date +%Y-%m-%d)"
mkdir -p "$OUT_DIR"

python3 - <<'PYEOF' "$DATA" "$OUT_DIR"
import json, sys, os
from datetime import datetime
polizas = json.load(open(sys.argv[1]))
hoy = datetime.now().date()
por_etapa = {"60_dias": [], "30_dias": [], "7_dias": []}
for p in polizas:
    venc = datetime.fromisoformat(p["vigencia_hasta"]).date()
    dias = (venc - hoy).days
    if dias == 60: por_etapa["60_dias"].append(p)
    elif dias == 30: por_etapa["30_dias"].append(p)
    elif dias == 7: por_etapa["7_dias"].append(p)
for etapa, items in por_etapa.items():
    if items:
        json.dump(items, open(f"{sys.argv[2]}/{etapa}.json", "w"), indent=2, ensure_ascii=False)
        print(f"✓ {len(items)} pólizas en etapa {etapa}")
PYEOF
