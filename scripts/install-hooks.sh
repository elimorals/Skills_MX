#!/usr/bin/env bash
# install-hooks.sh
# Instala los git hooks del repo (pre-commit principalmente).
#
# Uso:
#    bash scripts/install-hooks.sh           # instala
#    bash scripts/install-hooks.sh --remove  # desinstala

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [ "${1:-}" = "--remove" ]; then
    echo "→ Removiendo hooks..."
    rm -f .git/hooks/pre-commit
    echo "✓ Hooks removidos"
    exit 0
fi

echo "→ Instalando hooks de plugins-mx..."

# Pre-commit: symlink a scripts/pre-commit.sh
mkdir -p .git/hooks
ln -sf "../../scripts/pre-commit.sh" .git/hooks/pre-commit
chmod +x scripts/pre-commit.sh
chmod +x .git/hooks/pre-commit

echo "  ✓ pre-commit → scripts/pre-commit.sh"
echo ""
echo "Hooks activos:"
ls -la .git/hooks/ | grep -v sample | grep "^l" || echo "  (ninguno)"
echo ""
echo "Para saltarse temporalmente: git commit --no-verify"
echo "Para desinstalar: bash scripts/install-hooks.sh --remove"
