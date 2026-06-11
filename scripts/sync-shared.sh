#!/usr/bin/env bash
# sync-shared.sh
# Copia los skills de _shared/ a cada plugin vertical.
# Se ejecuta antes de cada release de plugin.
#
# Uso:
#   ./scripts/sync-shared.sh                    # Sync a todos los plugins detectados
#   ./scripts/sync-shared.sh core-mexico        # Sync solo a un plugin específico

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SHARED="$ROOT/_shared"

if [ ! -d "$SHARED" ]; then
  echo "❌ No existe $SHARED" >&2
  exit 1
fi

# Detectar plugins: cualquier directorio raíz con .claude-plugin/plugin.json
detect_plugins() {
  find "$ROOT" -maxdepth 2 -type d -name ".claude-plugin" -print0 | \
    xargs -0 -n1 dirname | \
    grep -v "^$ROOT/_shared" || true
}

sync_to_plugin() {
  local plugin_dir="$1"
  local plugin_name
  plugin_name="$(basename "$plugin_dir")"

  echo "→ Sincronizando _shared/ a $plugin_name"
  mkdir -p "$plugin_dir/skills"

  for skill_dir in "$SHARED"/*/; do
    [ -d "$skill_dir" ] || continue
    local skill_name
    skill_name="$(basename "$skill_dir")"

    # Solo sync si el plugin declara este skill en su plugin.json
    if grep -q "\"skills/$skill_name\"" "$plugin_dir/.claude-plugin/plugin.json" 2>/dev/null; then
      rsync -a --delete "$skill_dir" "$plugin_dir/skills/$skill_name/"
      echo "  ✓ $skill_name"
    fi
  done
}

if [ $# -gt 0 ]; then
  target="$ROOT/$1"
  if [ ! -d "$target/.claude-plugin" ]; then
    echo "❌ No es un plugin válido: $1" >&2
    exit 1
  fi
  sync_to_plugin "$target"
else
  while IFS= read -r plugin; do
    [ -n "$plugin" ] && sync_to_plugin "$plugin"
  done < <(detect_plugins)
fi

echo "✓ Sync completado."
