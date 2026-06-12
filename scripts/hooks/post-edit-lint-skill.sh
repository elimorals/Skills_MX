#!/usr/bin/env bash
# post-edit-lint-skill.sh — Claude Code PostToolUse hook
#
# Si la última operación fue Edit/Write sobre un SKILL.md → correr lint automático
# sobre ese skill. Si falla → alertar pero NO bloquear (es post).
#
# Disparado por: PostToolUse del tipo Edit/Write
# Recibe en stdin: JSON con info de la tool call ({tool, params, result})

set -u

source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

# Leer stdin (JSON de la tool call)
INPUT=$(cat 2>/dev/null || echo '{}')

# Extraer el path del archivo editado
FILE_PATH=$(echo "$INPUT" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    params = data.get('params', {})
    print(params.get('file_path', ''))
except Exception:
    pass
" 2>/dev/null || echo "")

# Solo procesar si fue un SKILL.md
if [[ "$FILE_PATH" != *"SKILL.md" ]]; then
  exit 0
fi

if [ ! -f "$FILE_PATH" ]; then
  exit 0
fi

# Lint mínimo: validar frontmatter
HEAD_FIRST_LINE=$(head -1 "$FILE_PATH")
if [ "$HEAD_FIRST_LINE" != "---" ]; then
  echo "⚠ post-edit-lint: $FILE_PATH no inicia con frontmatter ---"
  hook_log "post-edit-lint-skill" "warning" "frontmatter delimiter missing in $FILE_PATH"
  exit 0  # warning, no bloquea
fi

# Validar campos name + description
FRONTMATTER=$(awk '/^---$/{c++; next} c==1{print}' "$FILE_PATH")
NAME=$(echo "$FRONTMATTER" | awk -F': ' '/^name:/{print $2; exit}' | tr -d '"' | tr -d "'")
DESC=$(echo "$FRONTMATTER" | awk -F': ' '/^description:/{print $2; exit}')

if [ -z "$NAME" ]; then
  echo "⚠ post-edit-lint: $FILE_PATH sin campo 'name' en frontmatter"
  hook_log "post-edit-lint-skill" "warning" "name missing"
elif [ -z "$DESC" ] || [ ${#DESC} -lt 80 ]; then
  echo "⚠ post-edit-lint: $FILE_PATH description muy corta (<80 chars) para triggering robusto"
  hook_log "post-edit-lint-skill" "warning" "description too short"
else
  hook_log "post-edit-lint-skill" "success" "$FILE_PATH OK"
fi

exit 0
