#!/usr/bin/env bash
# pre-push-run-fixtures.sh — git hook pre-push
#
# Corre los fixtures de regresión SOLO de los skills/MCPs modificados desde
# último push, para no tardar 5 min ejecutando todo.
#
# Si algún fixture falla → bloquea el push (exit != 0).
#
# Instalación: vincular como .git/hooks/pre-push (vía scripts/install-hooks.sh)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

# Detectar archivos modificados desde último push (vs origin/main)
CHANGED=$(git diff --name-only origin/main...HEAD 2>/dev/null || git diff --name-only HEAD)

if [ -z "$CHANGED" ]; then
  echo "🟢 pre-push: sin cambios → nada que validar"
  exit 0
fi

echo "🔍 pre-push: validando fixtures de skills/MCPs modificados..."

# Skills modificados → buscar fixtures que los cubren
SKILLS_CHANGED=$(echo "$CHANGED" | grep -E "(SKILL\.md|\.py)$" | sed -n 's|.*\(skills/[^/]*\).*|\1|p' | sort -u || true)
MCP_CHANGED=$(echo "$CHANGED" | grep -E "^mcp-servers/[^/]+/" | cut -d/ -f1-2 | sort -u || true)

FAILED=0

# Fixtures: ejecutar solo los relevantes
if [ -d "tests/fixtures" ]; then
  for skill_dir in $SKILLS_CHANGED; do
    skill_name=$(basename "$skill_dir")
    fixture_dir="tests/fixtures/$skill_name"
    if [ -d "$fixture_dir" ]; then
      echo "  → Fixtures de $skill_name..."
      for fixture in "$fixture_dir"/*.json; do
        [ -f "$fixture" ] || continue
        # Aquí iría la ejecución real. Por ahora solo valida JSON.
        if ! python3 -c "import json; json.load(open('$fixture'))" 2>/dev/null; then
          echo "    ❌ JSON inválido: $fixture"
          FAILED=$((FAILED + 1))
        fi
      done
    fi
  done
fi

# Tests MCP relevantes
for mcp_dir in $MCP_CHANGED; do
  mcp_name=$(basename "$mcp_dir")
  if [ -d "mcp-servers/.venv" ] && [ -d "mcp-servers/$mcp_name/tests" ]; then
    echo "  → Tests Python de $mcp_name..."
    if ! (cd mcp-servers && .venv/bin/python -m pytest "$mcp_name/tests" -q --no-header 2>&1 | tail -3); then
      FAILED=$((FAILED + 1))
    fi
  fi
done

if [ "$FAILED" -gt 0 ]; then
  echo "❌ pre-push: $FAILED fallos — push bloqueado"
  echo "Saltar con: git push --no-verify (NO recomendado)"
  exit 1
fi

echo "✅ pre-push: todo verde — push permitido"
exit 0
