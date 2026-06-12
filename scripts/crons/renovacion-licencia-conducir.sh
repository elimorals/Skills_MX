#!/usr/bin/env bash
# renovacion-licencia-conducir.sh
# Cron 1° de cada mes 08:00: revisar licencias por vencer en próximos 60 días.
#
# Lee data/licencias-conducir.json con:
#   [{"titular": "...", "estado": "CDMX", "vencimiento": "2026-08-15", "tipo": "A|B|C"}]

set -euo pipefail
REPO="${PATH_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
DATA="$REPO/data/licencias-conducir.json"
OUT_DIR="$REPO/alertas/licencias/$(date +%Y-%m-%d)"
mkdir -p "$OUT_DIR"

[ ! -f "$DATA" ] && { echo "SKIP: $DATA no existe"; exit 0; }

python3 - <<'PYEOF' "$DATA" "$OUT_DIR/proximas.json"
import json, sys
from datetime import datetime, timedelta
licencias = json.load(open(sys.argv[1]))
hoy = datetime.now().date()
proximas = []
for l in licencias:
    venc = datetime.fromisoformat(l["vencimiento"]).date()
    dias = (venc - hoy).days
    if 0 <= dias <= 60:
        proximas.append({**l, "dias_restantes": dias, "urgencia": "alta" if dias < 14 else "media"})
if proximas:
    json.dump(proximas, open(sys.argv[2], "w"), indent=2, ensure_ascii=False)
    print(f"✓ {len(proximas)} licencias próximas a vencer")
PYEOF
