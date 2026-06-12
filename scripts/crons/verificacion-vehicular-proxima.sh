#!/usr/bin/env bash
# verificacion-vehicular-proxima.sh
# Cron 1° de mes 08:30: alertar verificaciones próximas según engomado.
set -euo pipefail
REPO="${PATH_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
DATA="$REPO/data/autos-usuario.json"
OUT_DIR="$REPO/alertas/verificacion/$(date +%Y-%m)"
mkdir -p "$OUT_DIR"

[ ! -f "$DATA" ] && exit 0

python3 - <<'PYEOF' "$DATA" "$OUT_DIR/proximas.json"
import json, sys
from datetime import datetime
ENGOMADO_MES_MAP = {  # engomado → meses verificación CDMX/EdoMex
    "amarillo": [1, 2, 7, 8],
    "rosa": [2, 3, 8, 9],
    "rojo": [3, 4, 9, 10],
    "verde": [4, 5, 10, 11],
    "azul": [5, 6, 11, 12],
}
autos = json.load(open(sys.argv[1]))
mes_actual = datetime.now().month
proximas = []
for auto in autos:
    eng = auto.get("engomado", "").lower()
    meses_verifica = ENGOMADO_MES_MAP.get(eng, [])
    if mes_actual in meses_verifica:
        proximas.append({**auto, "verifica_este_mes": True})
if proximas:
    json.dump(proximas, open(sys.argv[2], "w"), indent=2, ensure_ascii=False)
    print(f"✓ {len(proximas)} autos a verificar este mes")
PYEOF
