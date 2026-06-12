#!/usr/bin/env bash
# refresh-sat-listas-69.sh
# Cron semanal que descarga las listas públicas del SAT:
#   - 69-B Definitivos (EFOS confirmados)
#   - 69-B Presuntos (EFOS en proceso)
#   - 69 Incumplidos
#
# Los archivos se cachean por 24h en ~/.cache/plugins-mx/sat_portal/.
# Llamarlo semanal mantiene el cache fresco para due-diligence.
#
# Programar:
#    # Linux: lunes a las 9am
#    0 9 * * 1 cd /Users/elias/Documents/Trabajo/skills && bash scripts/refresh-sat-listas-69.sh >> /tmp/sat-listas.log 2>&1
#
#    # macOS: ver scripts/crons/com.plugins-mx.sat-listas.plist

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT/mcp-servers"

if [ ! -d ".venv" ]; then
    echo "⚠ .venv no existe — ejecutar setup primero"
    exit 1
fi

echo "[$(date +%Y-%m-%dT%H:%M:%S)] Refresh listas 69 y 69-B SAT"

.venv/bin/python -c "
import asyncio
import sys
sys.path.insert(0, '.')
from mp_sat_portal.client import SatPortalClient

async def main():
    c = SatPortalClient()

    print('  → Lista 69-B EFOS...')
    r1 = c.consultar_69b_efos()
    if r1.get('simulated'):
        print('    (mock) registros:', r1.get('total_registros', 0))
    else:
        print('    registros descargados:', r1.get('total_registros', 0))

    print('  → Lista 69 Incumplidos...')
    r2 = c.consultar_69_incumplidos()
    if r2.get('simulated'):
        print('    (mock) registros:', r2.get('total_registros', 0))
    else:
        print('    registros descargados:', r2.get('total_registros', 0))

asyncio.run(main())
"

echo "[$(date +%Y-%m-%dT%H:%M:%S)] ✓ Refresh completado"
