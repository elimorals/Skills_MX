#!/usr/bin/env bash
# check-multas-vehiculares.sh
# Cron diario 08:00: revisar multas nuevas en CDMX + EdoMex para autos del usuario.
#
# Espera archivo $PATH_REPO/data/autos-usuario.json con:
#   [{ "placas": "ABC123", "estado": "CDMX" }, ...]
#
# Por cada auto: invoca el MCP municipal correspondiente y persiste alertas.

set -euo pipefail

REPO="${PATH_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
DATA_FILE="$REPO/data/autos-usuario.json"
LOG_DIR="${LOG_DIR:-/tmp}"
OUT_DIR="$REPO/alertas/vehiculares/$(date +%Y-%m-%d)"

mkdir -p "$OUT_DIR"

if [ ! -f "$DATA_FILE" ]; then
  echo "$(date -Iseconds) - SKIP: $DATA_FILE no existe (sin autos registrados)"
  exit 0
fi

cd "$REPO/mcp-servers"

if [ ! -d ".venv" ]; then
  echo "$(date -Iseconds) - ERROR: venv no existe en mcp-servers/"
  exit 1
fi

PY="$REPO/mcp-servers/.venv/bin/python"

# Revisar cada auto
"$PY" - <<'PYEOF'
import json
import os
import sys
from pathlib import Path

repo = os.environ.get("PATH_REPO", str(Path(__file__).resolve().parents[2]))
data_file = Path(repo) / "data" / "autos-usuario.json"
out_dir = Path(repo) / "alertas" / "vehiculares" / __import__("datetime").datetime.now().strftime("%Y-%m-%d")
out_dir.mkdir(parents=True, exist_ok=True)

with open(data_file) as f:
    autos = json.load(f)

alertas_total = []
for auto in autos:
    placas = auto["placas"]
    estado = auto["estado"]
    try:
        # Importar MCP según estado
        if estado == "CDMX":
            from mp_cdmx_municipal.client import CdmxMunicipalClient
            client = CdmxMunicipalClient.from_env()
            res = client.consultar_multas_placa(placas)
        elif estado == "EdoMex":
            from mp_edomex_municipal.client import EdomexMunicipalClient
            client = EdomexMunicipalClient.from_env()
            res = client.consultar_multas_placa(placas)
        else:
            continue

        multas = res.get("multas", [])
        if multas:
            alertas_total.append({"placas": placas, "estado": estado, "multas": multas, "monto_total": sum(m.get("monto", 0) for m in multas)})
    except Exception as exc:
        print(f"{placas}: error {exc}", file=sys.stderr)

if alertas_total:
    out_path = out_dir / "multas-nuevas.json"
    out_path.write_text(json.dumps(alertas_total, indent=2, ensure_ascii=False))
    print(f"✓ {len(alertas_total)} autos con multas nuevas → {out_path}")
else:
    print("✓ Sin multas nuevas hoy")
PYEOF
