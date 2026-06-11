#!/usr/bin/env bash
# run-fixtures.sh
# Corre fixtures de regresión contra los scripts ejecutables locales.
#
# Uso:
#   ./scripts/run-fixtures.sh                  # Todos
#   ./scripts/run-fixtures.sh iva-retenciones-mx  # Solo un skill

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FIXTURES_DIR="$ROOT/tests/fixtures"
SKILL_FILTER="${1:-}"

PASS=0
FAIL=0
TOTAL=0

# Color output si terminal lo soporta
if [ -t 1 ]; then
  GREEN='\033[0;32m'
  RED='\033[0;31m'
  YELLOW='\033[0;33m'
  RESET='\033[0m'
else
  GREEN=''
  RED=''
  YELLOW=''
  RESET=''
fi

ok() { echo -e "  ${GREEN}✓${RESET} $1"; PASS=$((PASS+1)); }
fail() { echo -e "  ${RED}✗${RESET} $1"; FAIL=$((FAIL+1)); }
skip() { echo -e "  ${YELLOW}⊘${RESET} $1"; }

run_iva_retenciones() {
  local fixture="$1"
  TOTAL=$((TOTAL+1))
  local name=$(jq -r .name "$fixture")
  local input_emisor=$(jq -r '.input.emisor.regimen // ""' "$fixture")
  local input_receptor=$(jq -r '.input.receptor.regimen // ""' "$fixture")
  local input_monto=$(jq -r '.input.concepto.monto_base // 0' "$fixture")
  local expected_total=$(jq -r '.expected_output.total_comprobante // 0' "$fixture")
  local expected_neto=$(jq -r '.expected_output.neto_a_pagar_emisor // 0' "$fixture")

  # Filtrar casos especiales
  local extra_args=""
  if jq -e '.input.receptor.tipo == "extranjero"' "$fixture" > /dev/null; then
    extra_args="--exportacion --moneda USD --tc 18.5"
  fi

  if [ -n "$input_emisor" ] && [ -n "$input_receptor" ] && [ -n "$extra_args" == "" ]; then
    local result=$(python3 "$ROOT/scripts/calcular_iva_retenciones.py" \
      --emisor "$input_emisor" \
      --receptor "$input_receptor" \
      --monto "$input_monto" \
      --json 2>/dev/null || echo "{}")

    local actual_total=$(echo "$result" | jq -r '.total_comprobante // 0')
    local actual_neto=$(echo "$result" | jq -r '.neto_a_pagar_emisor // 0')

    if [ "$actual_total" = "$expected_total" ] && [ "$actual_neto" = "$expected_neto" ]; then
      ok "$name"
    else
      fail "$name (expected total=$expected_total neto=$expected_neto, got total=$actual_total neto=$actual_neto)"
    fi
  else
    skip "$name (caso especial, validación manual)"
  fi
}

run_rfc_validacion() {
  local fixture="$1"
  TOTAL=$((TOTAL+1))
  local name=$(jq -r .name "$fixture")
  local input=$(jq -r '.input // empty' "$fixture")
  local expected_valido=$(jq -r '.expected_output.valido_estructura // false' "$fixture")

  if [ -z "$input" ]; then
    skip "$name (sin input)"
    return
  fi

  local result=$(python3 "$ROOT/scripts/validar_rfc.py" --json "$input" 2>/dev/null || echo "[{}]")
  local actual_valido=$(echo "$result" | jq -r '.[0].valido_estructura // false')

  if [ "$actual_valido" = "$expected_valido" ]; then
    ok "$name"
  else
    fail "$name (expected valido=$expected_valido, got $actual_valido)"
  fi
}

run_cfdi_emision() {
  local fixture="$1"
  TOTAL=$((TOTAL+1))
  local name=$(jq -r .name "$fixture")

  # Solo casos con input completo de payload
  if jq -e '.input.emisor and .input.receptor and .input.conceptos' "$fixture" > /dev/null; then
    local payload=$(jq '.input' "$fixture")
    local result=$(echo "$payload" | python3 -c "
import sys, json
from scripts.mock_pac import MockPAC
pac = MockPAC()
payload = json.loads(sys.stdin.read())
print(json.dumps(pac.timbrar(payload)))
" 2>/dev/null || echo "{}")

    if echo "$result" | jq -e '.exito' > /dev/null 2>&1; then
      ok "$name"
    else
      local errores=$(echo "$result" | jq -r '.errores[]?' 2>/dev/null)
      fail "$name ($errores)"
    fi
  else
    skip "$name (caso de validación, requiere mock especializado)"
  fi
}

echo "Running fixtures..."
echo ""

# IVA retenciones
if [ -z "$SKILL_FILTER" ] || [ "$SKILL_FILTER" = "iva-retenciones-mx" ]; then
  if [ -d "$FIXTURES_DIR/iva-retenciones-mx" ]; then
    echo "iva-retenciones-mx:"
    for f in "$FIXTURES_DIR/iva-retenciones-mx"/*.json; do
      [ -f "$f" ] && run_iva_retenciones "$f"
    done
    echo ""
  fi
fi

# RFC validación
if [ -z "$SKILL_FILTER" ] || [ "$SKILL_FILTER" = "rfc-validacion" ]; then
  if [ -d "$FIXTURES_DIR/rfc-validacion" ]; then
    echo "rfc-validacion:"
    for f in "$FIXTURES_DIR/rfc-validacion"/*.json; do
      [ -f "$f" ] && run_rfc_validacion "$f"
    done
    echo ""
  fi
fi

# CFDI emisión (a través del mock PAC)
if [ -z "$SKILL_FILTER" ] || [ "$SKILL_FILTER" = "cfdi-emision" ]; then
  if [ -d "$FIXTURES_DIR/cfdi-emision" ]; then
    echo "cfdi-emision (via mock PAC):"
    for f in "$FIXTURES_DIR/cfdi-emision"/*.json; do
      [ -f "$f" ] && run_cfdi_emision "$f"
    done
    echo ""
  fi
fi

echo "─────────────────────────────"
echo "Total:  $TOTAL"
echo -e "Pass:   ${GREEN}$PASS${RESET}"
echo -e "Fail:   ${RED}$FAIL${RESET}"
[ "$FAIL" -gt 0 ] && exit 1 || exit 0
