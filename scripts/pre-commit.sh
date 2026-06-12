#!/usr/bin/env bash
# Pre-commit hook para plugins-mx.
#
# Valida antes de cada commit:
#  1. lint-skills.sh — todos los SKILL.md tienen frontmatter correcto
#  2. JSON válido en todos los .mcp.json y plugin.json
#  3. No commit de .env ni credenciales por accidente
#  4. Tests de MCPs si hay cambios en mcp-servers/
#
# Para instalar:
#    ln -sf ../../scripts/pre-commit.sh .git/hooks/pre-commit
#
# Para saltarse (no recomendado):
#    git commit --no-verify

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || { cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd; })"
cd "$REPO_ROOT"

echo "🔍 pre-commit: validando cambios..."

# ---------- 1. Detectar archivos staged ----------

# Usar -C explícito para asegurar que git busca en el repo correcto
STAGED=$(git -C "$REPO_ROOT" diff --cached --name-only --diff-filter=ACM 2>/dev/null || true)

if [ -z "$STAGED" ]; then
    echo "✓ Sin cambios staged. Skipping pre-commit checks."
    exit 0
fi

# ---------- 2. Prevenir commit de credenciales ----------

# Patrones que NUNCA deben commitearse
FORBIDDEN_PATTERNS=(
    "\.env$"
    "\.env\.[^e][^x][^a]"  # .env.local, .env.production — pero NO .env.example
    "secrets/"
    "\.pem$"
    "\.key$"
    "\.p12$"
    "\.cer$"
)

leaked=()
for f in $STAGED; do
    for pat in "${FORBIDDEN_PATTERNS[@]}"; do
        if [[ "$f" =~ $pat ]]; then
            leaked+=("$f")
        fi
    done
done

if [ ${#leaked[@]} -gt 0 ]; then
    echo "❌ Bloqueando commit — archivos con posibles credenciales:"
    for f in "${leaked[@]}"; do
        echo "    $f"
    done
    echo ""
    echo "  Si es legítimo (ej. .env.example), actualizar pre-commit.sh."
    echo "  Si es accidente, hacer: git restore --staged $f"
    exit 1
fi

# ---------- 3. Buscar literal de secrets en diff ----------

# Patrones de secrets típicos
SECRET_PATTERNS=(
    "FACTURAMA_USER=[a-zA-Z0-9]"
    "FACTURAMA_PASSWORD=[a-zA-Z0-9]"
    "BANXICO_TOKEN=[a-zA-Z0-9]"
    "MERCADOPAGO_ACCESS_TOKEN=(APP_USR|TEST)-[a-zA-Z0-9]"
    "CONEKTA_API_KEY=key_(test|live)_"
    "ML_REFRESH_TOKEN=[a-zA-Z0-9]"
    "SHOPIFY_ACCESS_TOKEN=shpat_"
    "BITSO_API_KEY=[a-zA-Z0-9]"
    "BITSO_API_SECRET=[a-zA-Z0-9]"
    # Genéricos
    "-----BEGIN (RSA |EC )?PRIVATE KEY-----"
    "aws_secret_access_key"
)

diff_output=$(git diff --cached -U0 || true)
for pat in "${SECRET_PATTERNS[@]}"; do
    if echo "$diff_output" | grep -E "$pat" > /dev/null 2>&1; then
        echo "❌ Bloqueando commit — posible secret en diff:"
        echo "    patrón: $pat"
        echo "  Revisar y eliminar antes de commit."
        exit 1
    fi
done

# ---------- 4. Lint de SKILL.md si hay cambios ----------

skill_changes=$(echo "$STAGED" | grep "SKILL\.md$" || true)
if [ -n "$skill_changes" ]; then
    echo "→ Lint de SKILL.md..."
    bash scripts/lint-skills.sh > /dev/null 2>&1 || {
        echo "❌ lint-skills.sh falló. Corre 'bash scripts/lint-skills.sh' para ver detalles."
        exit 1
    }
    echo "  ✓ lint-skills passed"
fi

# ---------- 5. Validar JSON de plugin.json y .mcp.json ----------

json_files=$(echo "$STAGED" | grep -E "(plugin\.json|\.mcp\.json)$" || true)
if [ -n "$json_files" ]; then
    echo "→ Validando JSON..."
    for f in $json_files; do
        if ! python3 -m json.tool "$f" > /dev/null 2>&1; then
            echo "❌ JSON inválido: $f"
            python3 -m json.tool "$f" 2>&1 | head -5
            exit 1
        fi
    done
    echo "  ✓ JSON válido"
fi

# ---------- 6. Tests de MCP-servers si cambian ----------

mcp_changes=$(echo "$STAGED" | grep "^mcp-servers/" || true)
if [ -n "$mcp_changes" ]; then
    echo "→ Tests MCP-servers..."
    if [ -d "mcp-servers/.venv" ]; then
        cd mcp-servers
        if ! .venv/bin/python -m pytest -q --no-header 2>&1 | tail -3 | grep -E "passed|warnings" > /dev/null; then
            echo "❌ MCP tests fallaron. Corre: cd mcp-servers && .venv/bin/python -m pytest"
            cd ..
            exit 1
        fi
        cd ..
        echo "  ✓ MCP tests pasaron"
    else
        echo "  ⚠ .venv no existe en mcp-servers/ — skip de tests"
    fi
fi

echo ""
echo "✓ pre-commit: todo OK."
exit 0
