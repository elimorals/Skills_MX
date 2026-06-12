#!/usr/bin/env bash
# validar-output-vs-schema.sh — Claude Code PreToolUse hook
#
# Antes de que un skill emita output (típicamente Write con JSON estructurado),
# valida que cumpla con su schema correspondiente en schemas/.
#
# Mapping skill → schema (por convención):
#   cotizacion-mxn → schemas/cotizacion-mxn-output.schema.json
#   propuesta-comercial → schemas/propuesta-comercial-output.schema.json
#   cobranza-seguimiento → schemas/cobranza-seguimiento-output.schema.json
#   garantia-servicio → schemas/garantia-servicio-output.schema.json
#   orden-trabajo → schemas/orden-trabajo-output.schema.json
#   etc.
#
# Si el output no cumple schema → BLOQUEA (exit 2) y reporta los errores.

set -u

source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

INPUT=$(cat 2>/dev/null || echo '{}')

# Detectar si es Write con un archivo JSON
FILE_PATH=$(echo "$INPUT" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    params = data.get('params', {})
    fp = params.get('file_path', '')
    if fp.endswith('.json'):
        print(fp)
except Exception:
    pass
" 2>/dev/null || echo "")

if [ -z "$FILE_PATH" ]; then
  exit 0
fi

CONTENT=$(echo "$INPUT" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(data.get('params', {}).get('content', ''))
except Exception:
    pass
" 2>/dev/null || echo "")

if [ -z "$CONTENT" ]; then
  exit 0
fi

# Detectar a qué skill corresponde el output basado en convención de path
# (ej: clientes/<rfc>/cotizacion.json → cotizacion-mxn)
SKILL_HINT=""
case "$FILE_PATH" in
  *cotizacion*.json) SKILL_HINT="cotizacion-mxn" ;;
  *propuesta*.json) SKILL_HINT="propuesta-comercial" ;;
  *cobranza*.json) SKILL_HINT="cobranza-seguimiento" ;;
  *garantia*.json) SKILL_HINT="garantia-servicio" ;;
  *orden-trabajo*.json|*OT-*.json) SKILL_HINT="orden-trabajo" ;;
  *constancia*.json) SKILL_HINT="constancias-academicas" ;;
  *reporte-mensual*.json) SKILL_HINT="reporte-mensual-cliente" ;;
  *due-diligence*.json) SKILL_HINT="due-diligence" ;;
  *ficha-cliente*.json) SKILL_HINT="ficha-cliente" ;;
  *) exit 0 ;;
esac

SCHEMA_PATH="$REPO_ROOT/schemas/${SKILL_HINT}-output.schema.json"
[ "$SKILL_HINT" = "ficha-cliente" ] && SCHEMA_PATH="$REPO_ROOT/schemas/ficha-cliente.schema.json"

if [ ! -f "$SCHEMA_PATH" ]; then
  # Sin schema → no validar
  exit 0
fi

# ⚠ Seguridad: pasar $CONTENT por archivo temporal — NUNCA interpolar en cuerpo Python.
# Heredoc con delimitador citado <<'PYEOF' deshabilita expansión $VAR / $(...) / backticks.
# Esto previene code injection si el output incluye triple comilla o expansión shell.
TMP_CONTENT=$(mktemp)
trap 'rm -f "$TMP_CONTENT"' EXIT
printf '%s' "$CONTENT" > "$TMP_CONTENT"

RESULT=$(python3 - "$SCHEMA_PATH" "$TMP_CONTENT" <<'PYEOF' 2>&1
import json
import sys
try:
    import jsonschema
except ImportError:
    print("jsonschema not installed — skipping validation")
    sys.exit(0)

schema_path = sys.argv[1]
content_path = sys.argv[2]

with open(content_path) as f:
    content = f.read()

with open(schema_path) as f:
    schema = json.load(f)

try:
    instance = json.loads(content)
except json.JSONDecodeError as e:
    print(f"❌ JSON inválido: {e}")
    sys.exit(2)

validator = jsonschema.Draft7Validator(schema)
errors = list(validator.iter_errors(instance))
if errors:
    print(f"❌ Output no cumple schema {schema_path}:")
    for e in errors[:5]:
        print(f"  - {e.path}: {e.message}")
    sys.exit(2)
print("✓ Output cumple schema")
PYEOF
)

EXIT_CODE=$?

if [ "$EXIT_CODE" = "2" ]; then
  echo "$RESULT"
  hook_log "validar-output-vs-schema" "blocked" "$SKILL_HINT: schema violation"
  exit 2
fi

hook_log "validar-output-vs-schema" "success" "$SKILL_HINT: OK"
exit 0
