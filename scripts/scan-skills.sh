#!/usr/bin/env bash
# scan-skills.sh — auditoría de seguridad de skills con NVIDIA SkillSpector en modo
# estático (--no-llm): el contenido de los skills no sale de la máquina. Solo SC4
# consulta OSV.dev con nombres de dependencias.
#
# Requiere: uv tool install git+https://github.com/NVIDIA/skillspector.git
# Uso:      ./scripts/scan-skills.sh [dir_salida]
# Sale con 1 si algún plugin supera risk score 50 (umbral de SkillSpector).

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${1:-${TMPDIR:-/tmp}/skillspector}"
mkdir -p "$OUT"
command -v skillspector >/dev/null || { echo "❌ skillspector no instalado" >&2; exit 2; }

fail=0
cd "$ROOT" || exit 2
for dir in _shared */skills; do
  [ -d "$dir" ] || continue
  name="${dir%/skills}"
  skillspector scan "$dir" --recursive --no-llm --format json --output "$OUT/$name.json" >/dev/null 2>&1
  rc=$?
  score="$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['max_risk_score'])" "$OUT/$name.json" 2>/dev/null || echo "?")"
  if [ "$rc" -ne 0 ]; then
    echo "✗ $name (risk $score, rc $rc)"
    fail=1
  else
    echo "✓ $name (risk $score)"
  fi
done
echo "Reportes JSON en $OUT"
exit $fail
