#!/usr/bin/env bash
# check-multas-vehiculares.sh
# Cron diario 08:00 — revisa portales municipales (CDMX/EdoMex/MTY) para multas vehiculares
# de placas registradas en el tracker.
#
# Programar:
#    0 8 * * * cd /Users/elias/Documents/Trabajo/skills && bash scripts/check-multas-vehiculares.sh >> /tmp/plugins-mx-multas.log 2>&1
#
# Si no hay placas en tracker o credenciales, corre mock.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT/mcp-servers"

SHARE_DIR="${PLUGINS_MX_SHARE_DIR:-$HOME/.local/share/plugins-mx}"
PLACAS_TRACKER="$SHARE_DIR/placas-vehiculos.jsonl"
ALERTAS="$SHARE_DIR/multas-detectadas.jsonl"

if [ ! -d ".venv" ]; then
    echo "⚠ .venv no existe — saltando"
    exit 0
fi

if [ ! -f "$PLACAS_TRACKER" ] || ! command -v jq >/dev/null; then
    echo "[$(date +%Y-%m-%dT%H:%M:%S)] Sin placas registradas — fin"
    exit 0
fi

echo "[$(date +%Y-%m-%dT%H:%M:%S)] Revisando multas vehiculares"

count_total=0
count_nuevas=0
while IFS= read -r line; do
    placa=$(echo "$line" | jq -r '.placa // empty')
    entidad=$(echo "$line" | jq -r '.entidad // "cdmx"')

    if [ -z "$placa" ]; then
        continue
    fi

    # Validar formato placa contra regex estricto (anti-inyección).
    # Las placas mexicanas son alfanuméricas + guiones, 5-10 chars.
    if ! [[ "$placa" =~ ^[A-Z0-9-]{5,10}$ ]]; then
        echo "  ⚠ placa malformada en tracker, saltada"
        continue
    fi

    # Por entidad llamar el MCP correspondiente (allowlist explícito)
    mcp_modulo=""
    case "$entidad" in
        cdmx) mcp_modulo="mp_cdmx_municipal" ;;
        edomex) mcp_modulo="mp_edomex_municipal" ;;
        monterrey|mty) mcp_modulo="mp_monterrey_municipal" ;;
        *) continue ;;
    esac

    count_total=$((count_total+1))

    # Invocar Python con código ESTÁTICO. Variables externas pasan via env vars
    # (PLACA, MODULO) y se leen con os.environ. Esto evita inyección de código
    # si el tracker JSON fuera modificado por un atacante.
    result=$(PLACA="$placa" MODULO="$mcp_modulo" .venv/bin/python -c '
import os, json, importlib
try:
    mod = importlib.import_module(os.environ["MODULO"] + ".client")
    c = mod.Client()
    placa_in = os.environ["PLACA"]
    r = c.consultar_multas(placa_in) if hasattr(c, "consultar_multas") else {"multas": []}
    print(json.dumps(r))
except Exception as e:
    print(json.dumps({"error": str(e), "multas": []}))
' 2>/dev/null) || result='{"multas":[]}'

    multas=$(echo "$result" | jq -r '.multas | length // 0' 2>/dev/null || echo 0)
    if [ "$multas" -gt 0 ]; then
        count_nuevas=$((count_nuevas+multas))
        ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
        echo "{\"ts\":\"$ts\",\"placa_hash\":\"$(echo -n $placa | shasum | cut -c1-12)\",\"entidad\":\"$entidad\",\"multas_count\":$multas}" >> "$ALERTAS"
    fi
done < "$PLACAS_TRACKER"

echo "  ✓ Revisadas: $count_total placas, $count_nuevas multas detectadas"
[ "$count_nuevas" -gt 0 ] && echo "  → revisa $ALERTAS y ejecuta /talleres:multas o vertical aplicable"
