#!/usr/bin/env bash
# Helpers comunes para todos los hooks de Claude Code (no git hooks).
#
# Convenciones:
# - exit 0 → continúa normal
# - exit 2 → blocking error (PreToolUse bloquea la tool call)
# - exit otro → warning, no bloquea pero se logea
#
# Stdout del hook se imprime ANTES de la tool call (PreToolUse) o DESPUÉS (PostToolUse).

set -u

# Skip global escape: usuario puede saltarse todos los hooks
if [ "${CLAUDE_SKIP_HOOKS:-0}" = "1" ]; then
    exit 0
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd 2>/dev/null || echo "$PWD")"
CACHE_DIR="${PLUGINS_MX_CACHE_DIR:-$HOME/.cache/plugins-mx}"
SHARE_DIR="${PLUGINS_MX_SHARE_DIR:-$HOME/.local/share/plugins-mx}"
HOOK_LOG="$SHARE_DIR/hooks/hook-events.jsonl"

mkdir -p "$(dirname "$HOOK_LOG")" 2>/dev/null || true

hook_log() {
    # Append-only log de cada disparo de hook.
    local hook_name="$1"
    local outcome="$2"
    local detail="${3:-}"
    local ts
    ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    printf '{"ts":"%s","hook":"%s","outcome":"%s","detail":"%s"}\n' \
        "$ts" "$hook_name" "$outcome" "$detail" >> "$HOOK_LOG" 2>/dev/null || true
}

# Lee el JSON que Claude Code pasa por stdin a un hook.
# Si no se puede parsear, retorna {} para que el hook sea idempotente.
hook_read_input() {
    if command -v jq >/dev/null 2>&1; then
        jq -c '.' 2>/dev/null || echo "{}"
    else
        cat
    fi
}

# Verifica si jq existe; si no, hace fallback silencioso.
require_jq_or_skip() {
    if ! command -v jq >/dev/null 2>&1; then
        hook_log "$1" "skipped_no_jq" "instalar jq con: brew install jq"
        exit 0
    fi
}

emit_info() {
    echo "ℹ $1"
}

emit_warning() {
    echo "⚠ $1" >&2
}

emit_error() {
    echo "✗ $1" >&2
}
