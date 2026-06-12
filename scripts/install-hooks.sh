#!/usr/bin/env bash
# install-hooks.sh
# Instala (a) git hooks tradicionales + (b) hooks runtime de Claude Code.
#
# Uso:
#    bash scripts/install-hooks.sh                 # instala todos
#    bash scripts/install-hooks.sh --remove        # desinstala git hooks
#    bash scripts/install-hooks.sh --git-only      # solo git hooks
#    bash scripts/install-hooks.sh --runtime-only  # solo runtime hooks
#    bash scripts/install-hooks.sh --check         # verifica instalación

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

install_git_hooks() {
    echo "→ Instalando git hooks..."
    mkdir -p .git/hooks
    ln -sf "../../scripts/pre-commit.sh" .git/hooks/pre-commit
    chmod +x scripts/pre-commit.sh
    chmod +x .git/hooks/pre-commit
    echo "  ✓ pre-commit → scripts/pre-commit.sh"
}

install_runtime_hooks() {
    echo "→ Configurando hooks runtime de Claude Code..."

    if [ ! -f ".claude/settings.json" ]; then
        echo "  ⚠ .claude/settings.json no existe — saltando"
        return
    fi

    # Hacer ejecutables todos los hooks
    chmod +x scripts/hooks/*.sh 2>/dev/null || true
    count=$(ls scripts/hooks/*.sh 2>/dev/null | grep -v -E '_lib|test-all' | wc -l | tr -d ' ')
    echo "  ✓ $count hooks ejecutables en scripts/hooks/"
    echo "  ✓ .claude/settings.json detectado (Claude Code los activa automáticamente)"

    # Test rápido (opcional, no falla si hay error)
    if [ -x "scripts/hooks/test-all-hooks.sh" ]; then
        if bash scripts/hooks/test-all-hooks.sh >/dev/null 2>&1; then
            echo "  ✓ smoke test: 18/18 hook calls OK"
        else
            echo "  ⚠ smoke test falló — ejecuta 'bash scripts/hooks/test-all-hooks.sh' para detalles"
        fi
    fi
}

check_install() {
    echo "→ Verificando instalación..."
    ok=0
    fail=0

    # Git hook
    if [ -L ".git/hooks/pre-commit" ] || [ -x ".git/hooks/pre-commit" ]; then
        echo "  ✓ git pre-commit"
        ok=$((ok+1))
    else
        echo "  ✗ git pre-commit NO instalado"
        fail=$((fail+1))
    fi

    # Runtime hooks
    if [ -f ".claude/settings.json" ]; then
        echo "  ✓ .claude/settings.json existe"
        ok=$((ok+1))
    else
        echo "  ✗ .claude/settings.json falta"
        fail=$((fail+1))
    fi

    count=$(ls scripts/hooks/*.sh 2>/dev/null | grep -v _lib | grep -v test-all | wc -l | tr -d ' ')
    if [ "$count" -ge 13 ]; then
        echo "  ✓ $count hooks runtime en scripts/hooks/"
        ok=$((ok+1))
    else
        echo "  ✗ solo $count hooks runtime (esperados ≥13)"
        fail=$((fail+1))
    fi

    echo ""
    echo "Resultado: $ok OK, $fail fallos"
    [ "$fail" -eq 0 ]
}

# --- Main ---
case "${1:-}" in
    --remove)
        echo "→ Removiendo git hooks (runtime hooks se quitan editando .claude/settings.json)..."
        rm -f .git/hooks/pre-commit
        echo "✓ git pre-commit removido"
        exit 0
        ;;
    --check)
        check_install
        exit $?
        ;;
    --git-only)
        install_git_hooks
        ;;
    --runtime-only)
        install_runtime_hooks
        ;;
    *)
        install_git_hooks
        echo ""
        install_runtime_hooks
        ;;
esac

echo ""
echo "Listo. Notas:"
echo "  - Saltar git hooks: git commit --no-verify"
echo "  - Saltar runtime hooks (1 vez): CLAUDE_SKIP_HOOKS=1 antes del comando"
echo "  - Desinstalar git: bash scripts/install-hooks.sh --remove"
echo "  - Verificar: bash scripts/install-hooks.sh --check"
