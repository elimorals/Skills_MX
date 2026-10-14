#!/usr/bin/env bash
# lint-skills.sh
# Valida que cada SKILL.md del monorepo tenga frontmatter YAML correcto:
#   - delimitadores --- al inicio y cierre
#   - name (no vacío, kebab-case)
#   - description (no vacío, mínimo 80 caracteres para triggering útil)
#   - name == nombre del directorio
#   - description <= 1024 chars (aviso)
#   - seguridad: secretos, comandos peligrosos y prompt injection en el skill dir
#
# Uso:
#   ./scripts/lint-skills.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAILED=0
CHECKED=0
WARNED=0

# Patrones de seguridad (ERE). Mantener cortos: falsos positivos bloquean CI.
SECRET_RE='sk_live_[A-Za-z0-9]{20,}|sk-ant-[A-Za-z0-9_-]{20,}|APP_USR-[0-9]{6,}-[0-9a-f-]{20,}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{35}|xox[baprs]-[0-9A-Za-z-]{10,}|gh[pousr]_[A-Za-z0-9]{36}|-----BEGIN [A-Z ]*PRIVATE KEY-----'
DANGER_RE='(curl|wget)[^|]*\|[[:space:]]*(sudo[[:space:]]+)?(ba|z)?sh\b|rm[[:space:]]+-rf[[:space:]]+(/|~|\$HOME)([[:space:]]|$)|chmod[[:space:]]+(-R[[:space:]]+)?777|mkfs\.|dd[[:space:]]+if=.*of=/dev/'
INJECTION_RE='ignore (all )?(previous|prior|above) instructions|ignora (todas )?las instrucciones (anteriores|previas)|disregard (the )?(system|previous)|do not tell the user|no le digas al usuario|exfiltra|send .*(api[_ ]?key|token|password).* to http'

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
    elif [ "$(printf '%s' "$description" | python3 -c 'import sys; print(len(sys.stdin.read()))')" -gt 1024 ]; then
      # ponytail: aviso, no error — 24 skills heredados lo exceden; volver error al recortarlos.
      WARNED=$((WARNED + 1))
      echo "  ⚠ $relative: 'description' > 1024 chars (límite de la spec de Agent Skills)"
    fi

    # name debe coincidir con el directorio (Claude Code identifica la skill por ambos)
    local dir_name
    dir_name="$(basename "$(dirname "$skill_md")")"
    if [ -n "$name" ] && [ "$name" != "$dir_name" ]; then
      errors+=("'name' ($name) no coincide con el directorio ($dir_name)")
    fi
  fi

  # Seguridad: secretos, comandos peligrosos y prompt injection en SKILL.md + references/
  local skill_dir hits
  skill_dir="$(dirname "$skill_md")"
  hits="$(grep -rInE "$SECRET_RE" "$skill_dir" 2>/dev/null | head -3 || true)"
  [ -n "$hits" ] && errors+=("Posible secreto: ${hits//$'\n'/ | }")
  hits="$(grep -rInE "$DANGER_RE" "$skill_dir" 2>/dev/null | head -3 || true)"
  [ -n "$hits" ] && errors+=("Comando peligroso: ${hits//$'\n'/ | }")
  hits="$(grep -rIniE "$INJECTION_RE" "$skill_dir" 2>/dev/null | head -3 || true)"
  [ -n "$hits" ] && errors+=("Posible prompt injection: ${hits//$'\n'/ | }")

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
done < <(find "$ROOT" -name "SKILL.md" -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "$ROOT/.claude/*" -print0)

echo
echo "─────────────────────────────"
echo "Revisados: $CHECKED"
echo "Fallidos:  $FAILED"
echo "Avisos:    $WARNED"

if [ "$FAILED" -gt 0 ]; then
  exit 1
fi
