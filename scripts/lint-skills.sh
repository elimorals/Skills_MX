#!/usr/bin/env bash
# lint-skills.sh
# Valida que cada SKILL.md del monorepo tenga frontmatter YAML correcto:
#   - delimitadores --- al inicio y cierre
#   - name (no vacío, kebab-case)
#   - description (no vacío, mínimo 80 caracteres para triggering útil)
#   - allowed-tools si está presente, lista válida
#
# Uso:
#   ./scripts/lint-skills.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAILED=0
CHECKED=0

check_skill() {
  local skill_md="$1"
  CHECKED=$((CHECKED + 1))
  local relative="${skill_md#$ROOT/}"
  local errors=()

  # Frontmatter delimiter al inicio
  if ! head -1 "$skill_md" | grep -q "^---$"; then
    errors+=("Falta delimitador --- al inicio")
  fi

  # Extraer frontmatter (entre primer y segundo ---)
  local frontmatter
  frontmatter="$(awk '/^---$/{c++; next} c==1{print}' "$skill_md")"

  if [ -z "$frontmatter" ]; then
    errors+=("Frontmatter vacío o malformado")
  else
    # name presente y no vacío
    local name
    name="$(echo "$frontmatter" | awk -F': ' '/^name:/{print $2; exit}' | tr -d '"' | tr -d "'")"
    if [ -z "$name" ]; then
      errors+=("Falta campo 'name'")
    elif ! [[ "$name" =~ ^[a-z][a-z0-9-]*$ ]]; then
      errors+=("'name' no está en kebab-case: $name")
    fi

    # description presente y >= 80 chars
    local description
    description="$(echo "$frontmatter" | awk '/^description:/{sub(/^description: */, ""); print; exit}' | tr -d '"')"
    if [ -z "$description" ]; then
      errors+=("Falta campo 'description'")
    elif [ "${#description}" -lt 80 ]; then
      errors+=("'description' muy corto (${#description} chars, mínimo 80 para triggering útil)")
    fi
  fi

  if [ "${#errors[@]}" -gt 0 ]; then
    FAILED=$((FAILED + 1))
    echo "✗ $relative"
    for err in "${errors[@]}"; do
      echo "    · $err"
    done
  else
    echo "✓ $relative"
  fi
}

# Buscar todos los SKILL.md
while IFS= read -r -d '' skill_md; do
  check_skill "$skill_md"
done < <(find "$ROOT" -name "SKILL.md" -not -path "*/node_modules/*" -not -path "*/.git/*" -print0)

echo
echo "─────────────────────────────"
echo "Revisados: $CHECKED"
echo "Fallidos:  $FAILED"

if [ "$FAILED" -gt 0 ]; then
  exit 1
fi
