#!/usr/bin/env bash
# efirma-vencimiento-90d.sh
# Cron semanal lunes 09:00: revisar e.firma del usuario, alertar si vence en < 90 días.
set -euo pipefail
REPO="${PATH_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
CERT="${SAT_EFIRMA_CERT:-}"
[ -z "$CERT" ] && { echo "SKIP: SAT_EFIRMA_CERT no configurado"; exit 0; }
[ ! -f "$CERT" ] && { echo "SKIP: $CERT no existe"; exit 0; }

cd "$REPO/mcp-servers"
PY=.venv/bin/python
[ ! -x "$PY" ] && { echo "SKIP: venv no instalado"; exit 0; }

$PY - <<'PYEOF'
from mp_sat_portal.efirma_loader import EfirmaLoader
loader = EfirmaLoader.from_env()
meta = loader.metadata()
dias = meta.days_until_expiry
if dias < 90:
    print(f"⚠ e.firma RFC {meta.rfc} vence en {dias} días — agendar cita SAT")
else:
    print(f"✓ e.firma vigente {dias} días restantes")
PYEOF
