#!/usr/bin/env bash
# refresh-banxico-tcs.sh
# Cron diario que refresca tipos de cambio DOF de Banxico en cache local.
#
# Refresca: USD/MXN, EUR/MXN, GBP/MXN, CAD/MXN, JPY/MXN
#
# Programar (macOS launchd o linux crontab):
#    # Linux: editar crontab con `crontab -e`
#    0 10 * * 1-5 cd /Users/elias/Documents/Trabajo/skills && bash scripts/refresh-banxico-tcs.sh >> /tmp/banxico-tcs.log 2>&1
#
#    # macOS: ver scripts/crons/com.plugins-mx.banxico-tcs.plist
#
# Sin BANXICO_TOKEN corre mock y no hace red.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT/mcp-servers"

if [ ! -d ".venv" ]; then
    echo "⚠ .venv no existe — ejecutar setup primero"
    exit 1
fi

ISO_DATE=$(date +%Y-%m-%d)
echo "[$(date +%Y-%m-%dT%H:%M:%S)] Refresh TCs Banxico para $ISO_DATE"

# Pares a refrescar
PAIRS=("usd_mxn" "eur_mxn" "gbp_mxn" "cad_mxn" "jpy_mxn")

for pair in "${PAIRS[@]}"; do
    echo "  → $pair"
    # Llamar al MCP via Python directo (no JSON-RPC)
    .venv/bin/python -c "
import asyncio
import sys
sys.path.insert(0, '.')
from mp_banxico.client import BanxicoClient

async def main():
    c = BanxicoClient()
    try:
        r = await c.get_tc_dof('$pair', fecha='$ISO_DATE')
        if r.get('simulated'):
            print('    (mock) TC:', r.get('rate', 'N/A'))
        else:
            print('    TC real:', r.get('rate', 'N/A'))
    except Exception as e:
        print(f'    error: {e}', file=sys.stderr)

asyncio.run(main())
" || echo "    ⚠ Falló $pair"
done

echo "[$(date +%Y-%m-%dT%H:%M:%S)] ✓ Refresh completado"
