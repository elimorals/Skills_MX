#!/usr/bin/env bash
# PreToolUse: valida payload CFDI antes de invocar mp_facturama_extendido__timbrar_cfdi.
# Bloquea (exit 2) si encuentra problemas críticos.
#
# Inputs (vía stdin, JSON):
# {
#   "tool_name": "mp_facturama_extendido__timbrar_cfdi",
#   "tool_input": { "rfc_receptor": "...", "subtotal": ..., "total": ..., ... }
# }

set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$SCRIPT_DIR/_lib.sh"

HOOK_NAME="pre-timbrado-validation"
require_jq_or_skip "$HOOK_NAME"

input=$(hook_read_input)

rfc=$(echo "$input" | jq -r '.tool_input.rfc_receptor // empty')
subtotal=$(echo "$input" | jq -r '.tool_input.subtotal // empty')
total=$(echo "$input" | jq -r '.tool_input.total // empty')
metodo=$(echo "$input" | jq -r '.tool_input.metodo_pago // empty')
forma=$(echo "$input" | jq -r '.tool_input.forma_pago // empty')

problems=()

# 1. RFC formato básico (12 PM / 13 PF, alfanumérico mayúscula)
if [ -z "$rfc" ]; then
    problems+=("RFC receptor vacío")
elif ! echo "$rfc" | grep -qE '^[A-ZÑ&]{3,4}[0-9]{6}[A-Z0-9]{3}$'; then
    problems+=("RFC formato inválido: $rfc")
fi

# 2. Totales presentes
if [ -z "$subtotal" ] || [ -z "$total" ]; then
    problems+=("subtotal o total faltante")
fi

# 3. PUE+99 (ME) prohibido (debe ser PUE+01 efectivo / 03 transferencia / etc.)
if [ "$metodo" = "PUE" ] && [ "$forma" = "99" ]; then
    problems+=("PUE+forma 99 (Por definir) no permitido — usa forma específica")
fi

# 4. PPD requiere forma 99 (por definir)
if [ "$metodo" = "PPD" ] && [ -n "$forma" ] && [ "$forma" != "99" ]; then
    problems+=("PPD requiere forma_pago=99 (Por definir)")
fi

if [ ${#problems[@]} -gt 0 ]; then
    emit_error "pre-timbrado-validation: ${#problems[@]} problema(s):"
    for p in "${problems[@]}"; do
        echo "  - $p" >&2
    done
    hook_log "$HOOK_NAME" "blocked" "${problems[*]}"
    exit 2
fi

emit_info "pre-timbrado-validation: payload OK (RFC $rfc, total $total, $metodo+$forma)"
hook_log "$HOOK_NAME" "passed" "rfc_hash=$(echo -n "$rfc" | shasum | cut -c1-12)"
exit 0
