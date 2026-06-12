#!/usr/bin/env bash
# Smoke test de los 13 hooks: dispara cada uno con un payload sintético y
# verifica que NO devuelvan exit code distinto de 0 o 2.
#
# Uso: bash scripts/hooks/test-all-hooks.sh

set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

failed=()

run_hook() {
    local hook="$1"
    local stdin_json="$2"
    local expected_exit="${3:-0}"

    actual=$(echo "$stdin_json" | bash "$SCRIPT_DIR/$hook" 2>&1; echo "::exit_code=$?")
    exit_code=$(echo "$actual" | grep -o '::exit_code=[0-9]*' | grep -o '[0-9]*')

    if [ "$exit_code" = "$expected_exit" ]; then
        echo "✓ $hook (exit=$exit_code)"
    else
        echo "✗ $hook  (esperado=$expected_exit, actual=$exit_code)"
        failed+=("$hook")
    fi
}

echo "===== Smoke test 13 hooks ====="

# --- PreToolUse ---
run_hook pre-timbrado-validation.sh \
    '{"tool_name":"mp_facturama_extendido__timbrar_cfdi","tool_input":{"rfc_receptor":"XAXX010101000","subtotal":100,"total":116,"metodo_pago":"PUE","forma_pago":"03"}}' \
    0

run_hook pre-timbrado-validation.sh \
    '{"tool_name":"mp_facturama_extendido__timbrar_cfdi","tool_input":{"rfc_receptor":"bad","subtotal":100,"total":116}}' \
    2

run_hook confirmar-envio-masivo-wa.sh \
    '{"tool_name":"mp_meta_whatsapp__send_message_batch","tool_input":{"destinatarios":["521..."]}}' \
    0

# >50 destinatarios → warning pero exit 0
many=$(python3 -c 'import json;print(json.dumps({"tool_name":"mp_meta_whatsapp__send_message_batch","tool_input":{"destinatarios":["x"]*60}}))')
run_hook confirmar-envio-masivo-wa.sh "$many" 0

run_hook validar-cfdi-payload.sh \
    '{"tool_name":"mp_facturama_extendido__timbrar_cfdi","tool_input":{"x":1}}' \
    0

run_hook validar-cfdi-payload.sh '{}' 2

run_hook validar-ficha-cliente.sh \
    '{"tool_name":"Write","tool_input":{"file_path":"foo/clientes/abc.json","content":"{\"rfc\":\"XAXX010101000\",\"nombre\":\"X\",\"email\":\"a@b.c\",\"tel\":\"1\"}"}}' \
    0

run_hook bitacora-mcp-calls.sh \
    '{"tool_name":"mp_banxico__tipo_cambio","tool_input":{}}' \
    0

# --- PostToolUse ---
run_hook backup-cfdi-automatico.sh \
    '{"tool_name":"mp_facturama_extendido__timbrar_cfdi","tool_result":{"uuid":"ABCD-1234"}}' \
    0

run_hook alert-cancelaciones-frecuentes.sh \
    '{"tool_name":"mp_facturama_extendido__cancelar_cfdi","tool_input":{"uuid":"ABC"}}' \
    0

run_hook actualizar-tc-banxico.sh \
    '{"tool_name":"mp_banxico__tipo_cambio"}' \
    0

run_hook sincronizar-shared-post-edit.sh \
    '{"tool_name":"Edit","tool_input":{"file_path":"foo/_shared/x.md"}}' \
    0

# --- SessionStart ---
run_hook contexto-inicial-sesion.sh '{}' 0
run_hook dashboard-cobranza-pendiente.sh '{}' 0
run_hook alerta-pago-provisional.sh '{}' 0
run_hook cfdi-vencimientos.sh '{}' 0

# --- Stop ---
run_hook cleanup-sesion.sh '{}' 0

# --- Skip global ---
CLAUDE_SKIP_HOOKS=1 run_hook pre-timbrado-validation.sh \
    '{"tool_input":{"rfc_receptor":"bad"}}' \
    0

echo ""
if [ ${#failed[@]} -eq 0 ]; then
    echo "✓✓✓ Todos los hooks pasaron"
    exit 0
else
    echo "✗ Fallaron ${#failed[@]}: ${failed[*]}"
    exit 1
fi
