#!/usr/bin/env bash
# version-bump.sh — bumpa versión de un plugin (semver).
#
# Uso:
#   ./scripts/version-bump.sh <plugin> patch|minor|major
#
# Ejemplos:
#   ./scripts/version-bump.sh freelancers-mx patch
#   ./scripts/version-bump.sh core-mexico minor
#   ./scripts/version-bump.sh agencia-marketing-mx major

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ $# -lt 2 ]; then
  echo "Uso: $0 <plugin> patch|minor|major"
  echo ""
  echo "Plugins disponibles:"
  for d in "$ROOT"/*/.claude-plugin/plugin.json; do
    [ -f "$d" ] && basename "$(dirname "$(dirname "$d")")"
  done
  exit 1
fi

PLUGIN="$1"
BUMP="$2"
PLUGIN_JSON="$ROOT/$PLUGIN/.claude-plugin/plugin.json"

if [ ! -f "$PLUGIN_JSON" ]; then
  echo "No existe plugin: $PLUGIN"
  exit 1
fi

if ! [[ "$BUMP" =~ ^(patch|minor|major)$ ]]; then
  echo "Bump inválido: $BUMP (use patch, minor o major)"
  exit 1
fi

if ! command -v jq > /dev/null; then
  echo "Requiere jq. Instalar con: brew install jq"
  exit 1
fi

CURRENT=$(jq -r .version "$PLUGIN_JSON")
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT"

case "$BUMP" in
  patch)
    PATCH=$((PATCH + 1))
    ;;
  minor)
    MINOR=$((MINOR + 1))
    PATCH=0
    ;;
  major)
    MAJOR=$((MAJOR + 1))
    MINOR=0
    PATCH=0
    ;;
esac

NEW_VERSION="${MAJOR}.${MINOR}.${PATCH}"

# Actualizar plugin.json
TMP=$(mktemp)
jq ".version = \"$NEW_VERSION\"" "$PLUGIN_JSON" > "$TMP" && mv "$TMP" "$PLUGIN_JSON"

echo "✓ $PLUGIN: $CURRENT → $NEW_VERSION"

# Actualizar CHANGELOG si existe
CHANGELOG="$ROOT/$PLUGIN/CHANGELOG.md"
if [ -f "$CHANGELOG" ]; then
  # Buscar [Unreleased] y reemplazar con la nueva versión
  TODAY=$(date +%Y-%m-%d 2>/dev/null || echo "YYYY-MM-DD")
  TMP=$(mktemp)
  awk -v ver="$NEW_VERSION" -v date="$TODAY" '
    /^## \[Unreleased\]/ {
      print "## [Unreleased]"
      print ""
      print "## [" ver "] — " date
      next
    }
    { print }
  ' "$CHANGELOG" > "$TMP" && mv "$TMP" "$CHANGELOG"
  echo "✓ CHANGELOG actualizado"
fi

echo ""
echo "Siguientes pasos:"
echo "1. Revisar cambios: git diff $PLUGIN_JSON"
[ -f "$CHANGELOG" ] && echo "2. Revisar CHANGELOG: git diff $CHANGELOG"
echo "3. Commit: git add $PLUGIN_JSON $CHANGELOG && git commit -m 'chore($PLUGIN): bump to $NEW_VERSION'"
echo "4. Tag: git tag $PLUGIN-v$NEW_VERSION"
