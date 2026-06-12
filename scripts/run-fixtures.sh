#!/usr/bin/env bash
# run-fixtures.sh
# Corre fixtures de regresión contra los scripts ejecutables locales.
#
# Uso:
#   ./scripts/run-fixtures.sh                    # Todos los handlers
#   ./scripts/run-fixtures.sh iva-retenciones-mx # Solo un skill
#   ./scripts/run-fixtures.sh --coverage         # Reporte cobertura solamente

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FIXTURES_DIR="$ROOT/tests/fixtures"
SKILL_FILTER="${1:-}"

PASS=0
FAIL=0
SKIP=0
TOTAL=0

# Color output si terminal lo soporta
if [ -t 1 ]; then
  GREEN='\033[0;32m'
  RED='\033[0;31m'
  YELLOW='\033[0;33m'
  BLUE='\033[0;34m'
  RESET='\033[0m'
else
  GREEN=''; RED=''; YELLOW=''; BLUE=''; RESET=''
fi

ok()    { echo -e "  ${GREEN}✓${RESET} $1"; PASS=$((PASS+1)); }
fail()  { echo -e "  ${RED}✗${RESET} $1"; FAIL=$((FAIL+1)); }
skip()  { echo -e "  ${YELLOW}⊘${RESET} $1"; SKIP=$((SKIP+1)); }
note()  { echo -e "  ${BLUE}ℹ${RESET} $1"; }

# ─────────────────────────────────────────────────────────────
# Handler genérico: validar estructura JSON del fixture
# Para skills sin handler ejecutable: solo verifica que el fixture
# tenga name + input + expected_output. Cuenta como PASS si OK.
# ─────────────────────────────────────────────────────────────
run_generic_validate() {
  local fixture="$1"
  TOTAL=$((TOTAL+1))
  local name
  name=$(jq -r '.name // "(sin nombre)"' "$fixture" 2>/dev/null || echo "$(basename "$fixture")")

  if ! python3 -c "import json; json.load(open('$fixture'))" 2>/dev/null; then
    fail "$name (JSON inválido)"
    return
  fi

  if ! jq -e '.name' "$fixture" > /dev/null 2>&1; then
    skip "$name (sin campo 'name')"
    return
  fi
  if ! jq -e '.input // .input_describe' "$fixture" > /dev/null 2>&1; then
    skip "$name (sin 'input')"
    return
  fi
  if ! jq -e '.expected_output // .expected_output_approximate // .expected' "$fixture" > /dev/null 2>&1; then
    skip "$name (sin 'expected_output')"
    return
  fi

  local n_validations
  n_validations=$(jq -r '.validations | length // 0' "$fixture" 2>/dev/null || echo "0")

  if [ "$n_validations" -gt 0 ]; then
    note "$name (estructura OK — $n_validations validaciones requieren ejecución del skill)"
  else
    note "$name (estructura OK)"
  fi
  PASS=$((PASS+1))
}

run_iva_retenciones() {
  local fixture="$1"
  TOTAL=$((TOTAL+1))
  local name
  name=$(jq -r .name "$fixture")
  local input_emisor
  input_emisor=$(jq -r '.input.emisor.regimen // ""' "$fixture")
  local input_receptor
  input_receptor=$(jq -r '.input.receptor.regimen // ""' "$fixture")
  local input_monto
  input_monto=$(jq -r '.input.concepto.monto_base // 0' "$fixture")
  local expected_total
  expected_total=$(jq -r '.expected_output.total_comprobante // 0' "$fixture")
  local expected_neto
  expected_neto=$(jq -r '.expected_output.neto_a_pagar_emisor // 0' "$fixture")

  if jq -e '.input.receptor.tipo == "extranjero"' "$fixture" > /dev/null; then
    skip "$name (extranjero)"
    return
  fi

  if [ -n "$input_emisor" ] && [ -n "$input_receptor" ]; then
    local result
    result=$(python3 "$ROOT/scripts/calcular_iva_retenciones.py" \
      --emisor "$input_emisor" \
      --receptor "$input_receptor" \
      --monto "$input_monto" \
      --json 2>/dev/null || echo "{}")

    local actual_total
    actual_total=$(echo "$result" | jq -r '.total_comprobante // 0')
    local actual_neto
    actual_neto=$(echo "$result" | jq -r '.neto_a_pagar_emisor // 0')

    if [ "$actual_total" = "$expected_total" ] && [ "$actual_neto" = "$expected_neto" ]; then
      ok "$name"
    else
      fail "$name (expected total=$expected_total neto=$expected_neto, got total=$actual_total neto=$actual_neto)"
    fi
  else
    skip "$name (caso especial)"
  fi
}

run_rfc_validacion() {
  local fixture="$1"
  TOTAL=$((TOTAL+1))
  local name
  name=$(jq -r .name "$fixture")
  local input
  input=$(jq -r '.input // empty' "$fixture")
  local expected_valido
  expected_valido=$(jq -r '.expected_output.valido_estructura // false' "$fixture")

  if [ -z "$input" ]; then
    skip "$name (sin input)"
    return
  fi

  local result
  result=$(python3 "$ROOT/scripts/validar_rfc.py" --json "$input" 2>/dev/null || echo "[{}]")
  local actual_valido
  actual_valido=$(echo "$result" | jq -r '.[0].valido_estructura // false')

  if [ "$actual_valido" = "$expected_valido" ]; then
    ok "$name"
  else
    fail "$name (expected valido=$expected_valido, got $actual_valido)"
  fi
}

run_cfdi_emision() {
  local fixture="$1"
  TOTAL=$((TOTAL+1))
  local name
  name=$(jq -r .name "$fixture")

  if jq -e '.input.emisor and .input.receptor and .input.conceptos' "$fixture" > /dev/null; then
    local payload
    payload=$(jq '.input' "$fixture")
    local result
    result=$(echo "$payload" | python3 -c "
import sys, json
from scripts.mock_pac import MockPAC
pac = MockPAC()
payload = json.loads(sys.stdin.read())
print(json.dumps(pac.timbrar(payload)))
" 2>/dev/null || echo "{}")

    if echo "$result" | jq -e '.exito' > /dev/null 2>&1; then
      ok "$name"
    else
      local errores
      errores=$(echo "$result" | jq -r '.errores[]?' 2>/dev/null)
      fail "$name ($errores)"
    fi
  else
    skip "$name (caso de validación)"
  fi
}

# Discovery automático por skill directory + handler mapping
run_skill_dir() {
  local skill_dir="$1"
  local skill_name
  skill_name=$(basename "$skill_dir")

  if [ -n "$SKILL_FILTER" ] && [ "$SKILL_FILTER" != "--coverage" ] && [ "$SKILL_FILTER" != "$skill_name" ]; then
    return
  fi

  echo "${skill_name}:"
  local handler="run_generic_validate"

  case "$skill_name" in
    iva-retenciones-mx)   handler="run_iva_retenciones" ;;
    rfc-validacion)       handler="run_rfc_validacion" ;;
    cfdi-emision)         handler="run_cfdi_emision" ;;
  esac

  local n=0
  for f in "$skill_dir"/*.json; do
    [ -f "$f" ] || continue
    $handler "$f"
    n=$((n+1))
  done

  if [ "$n" -eq 0 ]; then
    note "(sin fixtures en este directorio)"
  fi
  echo ""
}

report_coverage() {
  echo ""
  echo "── Cobertura de fixtures ──"
  local total_skills=0
  local with_fixtures=0
  local without_fixtures=()

  while IFS= read -r skill_path; do
    total_skills=$((total_skills+1))
    local skill_dir
    skill_dir=$(dirname "$skill_path")
    local skill_name
    skill_name=$(basename "$skill_dir")
    if [ -d "$FIXTURES_DIR/$skill_name" ] && ls "$FIXTURES_DIR/$skill_name"/*.json >/dev/null 2>&1; then
      with_fixtures=$((with_fixtures+1))
    else
      without_fixtures+=("$skill_name")
    fi
  done < <(find "$ROOT" -name "SKILL.md" -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null)

  local pct=0
  if [ "$total_skills" -gt 0 ]; then
    pct=$((with_fixtures * 100 / total_skills))
  fi

  echo "Skills totales: $total_skills"
  echo "Con fixtures:   $with_fixtures (${pct}%)"
  echo "Sin fixtures:   $((total_skills - with_fixtures))"

  if [ "${#without_fixtures[@]}" -le 30 ] && [ "${#without_fixtures[@]}" -gt 0 ]; then
    echo ""
    echo "Skills sin fixtures:"
    for s in "${without_fixtures[@]}"; do
      echo "  - $s"
    done
  fi
}

# Main
if [ "$SKILL_FILTER" = "--coverage" ]; then
  report_coverage
  exit 0
fi

echo "Running fixtures..."
echo ""

for skill_dir in "$FIXTURES_DIR"/*/; do
  [ -d "$skill_dir" ] || continue
  run_skill_dir "$skill_dir"
done

echo "─────────────────────────────"
echo "Total:  $TOTAL"
echo -e "Pass:   ${GREEN}$PASS${RESET}"
echo -e "Fail:   ${RED}$FAIL${RESET}"
echo -e "Skip:   ${YELLOW}$SKIP${RESET}"
echo ""

report_coverage

[ "$FAIL" -gt 0 ] && exit 1 || exit 0
