#!/usr/bin/env bash
# health-check.sh — reporte unificado de salud del proyecto plugins-mx
#
# Recorre todo el monorepo y reporta:
# - Conteo de cada artefacto (plugins, skills, MCPs, workflows, hooks, crons, evals, fixtures)
# - Cobertura: fixtures, evals, schemas vs skills
# - Sincronización _shared/ vs plugins verticales
# - Vencimientos próximos (e.firma, certs, licencias)
# - Secrets accidentalmente staged
# - Tests Python que rompen
# - Lint de skills
# - JSON inválidos
#
# Uso:
#   bash scripts/health-check.sh              # Reporte completo
#   bash scripts/health-check.sh --quick      # Sin tests Python (rápido)
#   bash scripts/health-check.sh --json       # Output JSON (CI-friendly)

set -o pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODE="${1:-full}"

# Colores
if [ -t 1 ] && [ "$MODE" != "--json" ]; then
  GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[0;33m'; BLUE='\033[0;34m'; BOLD='\033[1m'; RESET='\033[0m'
else
  GREEN=''; RED=''; YELLOW=''; BLUE=''; BOLD=''; RESET=''
fi

# Acumuladores — usamos archivo tmp en lugar de declare -A para portar bash 3 (macOS)
METRICS_FILE=$(mktemp)
trap 'rm -f "$METRICS_FILE"' EXIT
ERRORS=0
WARNINGS=0

metric() {
  echo "$1=$2" >> "$METRICS_FILE"
}

section() {
  [ "$MODE" = "--json" ] && return
  echo ""
  echo -e "${BOLD}── $1 ──${RESET}"
}

ok()   { [ "$MODE" = "--json" ] && return; echo -e "  ${GREEN}✓${RESET} $1"; }
warn() { [ "$MODE" = "--json" ] && return; echo -e "  ${YELLOW}⚠${RESET} $1"; WARNINGS=$((WARNINGS+1)); }
err()  { [ "$MODE" = "--json" ] && return; echo -e "  ${RED}✗${RESET} $1"; ERRORS=$((ERRORS+1)); }
info() { [ "$MODE" = "--json" ] && return; echo -e "  ${BLUE}ℹ${RESET} $1"; }

# ─────────────────────────────────────────────────────────────
# 1. Inventario
# ─────────────────────────────────────────────────────────────
section "Inventario"

PLUGINS=$(find "$ROOT" -maxdepth 3 -name "plugin.json" 2>/dev/null | wc -l | tr -d ' ')
SKILLS=$(find "$ROOT" -name "SKILL.md" -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null | wc -l | tr -d ' ')
SHARED_SKILLS=$(find "$ROOT/_shared" -name "SKILL.md" 2>/dev/null | wc -l | tr -d ' ')
MCPS=$(find "$ROOT/mcp-servers" -maxdepth 1 -type d -name "mp_*" 2>/dev/null | wc -l | tr -d ' ')
WORKFLOWS=$(find "$ROOT" -name "*.workflow.js" 2>/dev/null | wc -l | tr -d ' ')
HOOKS_RUNTIME=$(find "$ROOT/scripts/hooks" -name "*.sh" -not -name "_*" -not -name "test-*" 2>/dev/null | wc -l | tr -d ' ')
CRONS=$(find "$ROOT/scripts/crons" -name "*.sh" 2>/dev/null | wc -l | tr -d ' ')
EVALS=$(find "$ROOT/evals" -name "*.eval.json" 2>/dev/null | wc -l | tr -d ' ')
FIXTURES=$(find "$ROOT/tests/fixtures" -name "*.json" 2>/dev/null | wc -l | tr -d ' ')
SCHEMAS=$(find "$ROOT/schemas" -name "*.json" 2>/dev/null | wc -l | tr -d ' ')
SPECS=$(find "$ROOT/docs/specs" -name "*.md" -not -name "README*" -not -name "_template*" 2>/dev/null | wc -l | tr -d ' ')

ok "Plugins verticales: $PLUGINS"
ok "Skills (SKILL.md): $SKILLS  (de los cuales $SHARED_SKILLS en _shared/)"
ok "MCP servers: $MCPS"
ok "Workflows ejecutables: $WORKFLOWS"
ok "Hooks runtime CC: $HOOKS_RUNTIME"
ok "Crons scriptados: $CRONS"
ok "Evals (.eval.json): $EVALS"
ok "Fixtures: $FIXTURES"
ok "Schemas JSON: $SCHEMAS"
ok "Specs detallados: $SPECS"

metric plugins "$PLUGINS"
metric skills "$SKILLS"
metric mcps "$MCPS"
metric workflows "$WORKFLOWS"
metric hooks "$HOOKS_RUNTIME"
metric crons "$CRONS"
metric evals "$EVALS"
metric fixtures "$FIXTURES"
metric schemas "$SCHEMAS"
metric specs "$SPECS"

# ─────────────────────────────────────────────────────────────
# 2. Cobertura
# ─────────────────────────────────────────────────────────────
section "Cobertura"

# Skills con fixtures
SKILLS_WITH_FIXTURES=0
SKILLS_WITHOUT_FIXTURES=()
while IFS= read -r skill_path; do
  skill_name=$(basename "$(dirname "$skill_path")")
  if [ -d "$ROOT/tests/fixtures/$skill_name" ] && ls "$ROOT/tests/fixtures/$skill_name"/*.json >/dev/null 2>&1; then
    SKILLS_WITH_FIXTURES=$((SKILLS_WITH_FIXTURES+1))
  else
    SKILLS_WITHOUT_FIXTURES+=("$skill_name")
  fi
done < <(find "$ROOT" -name "SKILL.md" -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null)

FIX_PCT=0
[ "$SKILLS" -gt 0 ] && FIX_PCT=$((SKILLS_WITH_FIXTURES * 100 / SKILLS))

if [ "$FIX_PCT" -ge 50 ]; then ok "Skills con fixtures: $SKILLS_WITH_FIXTURES/$SKILLS (${FIX_PCT}%)"
elif [ "$FIX_PCT" -ge 25 ]; then warn "Skills con fixtures: $SKILLS_WITH_FIXTURES/$SKILLS (${FIX_PCT}%) — objetivo 50%"
else err "Skills con fixtures: $SKILLS_WITH_FIXTURES/$SKILLS (${FIX_PCT}%) — muy bajo, objetivo 50%"; fi

metric fixtures_coverage_pct "$FIX_PCT"

# Skills con evals
SKILLS_WITH_EVALS=$(find "$ROOT/evals" -name "*.eval.json" -exec basename {} .eval.json \; 2>/dev/null | sort -u | wc -l | tr -d ' ')
EVAL_PCT=0
[ "$SKILLS" -gt 0 ] && EVAL_PCT=$((SKILLS_WITH_EVALS * 100 / SKILLS))

if [ "$EVAL_PCT" -ge 80 ]; then ok "Skills con evals: $SKILLS_WITH_EVALS/$SKILLS (${EVAL_PCT}%)"
elif [ "$EVAL_PCT" -ge 50 ]; then warn "Skills con evals: $SKILLS_WITH_EVALS/$SKILLS (${EVAL_PCT}%) — objetivo 80%"
else err "Skills con evals: $SKILLS_WITH_EVALS/$SKILLS (${EVAL_PCT}%) — muy bajo, objetivo 80%"; fi

metric evals_coverage_pct "$EVAL_PCT"

# ─────────────────────────────────────────────────────────────
# 3. Sincronización _shared/
# ─────────────────────────────────────────────────────────────
section "Sincronización _shared/"

DESYNC=0
for shared in "$ROOT/_shared"/*/; do
  [ -d "$shared" ] || continue
  shared_name=$(basename "$shared")
  for plugin in "$ROOT"/*/; do
    plugin_name=$(basename "$plugin")
    [ "$plugin_name" = "_shared" ] && continue
    [ "$plugin_name" = "mcp-servers" ] && continue
    [ "$plugin_name" = "scripts" ] && continue
    [ "$plugin_name" = "docs" ] && continue
    [ "$plugin_name" = "tests" ] && continue
    [ "$plugin_name" = "schemas" ] && continue
    [ "$plugin_name" = "evals" ] && continue
    [ "$plugin_name" = "webhooks" ] && continue
    if [ -f "$plugin/skills/$shared_name/SKILL.md" ]; then
      if ! diff -q "$shared/SKILL.md" "$plugin/skills/$shared_name/SKILL.md" >/dev/null 2>&1; then
        DESYNC=$((DESYNC+1))
      fi
    fi
  done
done

if [ "$DESYNC" -eq 0 ]; then ok "Skills _shared/ sincronizados en todos los plugins"
else warn "$DESYNC skills _shared/ desincronizados — correr scripts/sync-shared.sh"; fi

metric shared_desync "$DESYNC"

# ─────────────────────────────────────────────────────────────
# 4. Secretos accidentales
# ─────────────────────────────────────────────────────────────
section "Secretos staged"

SECRETOS=0
PATTERNS=(
  'sk_live_[a-zA-Z0-9]{20,}'
  'APP_USR-[a-zA-Z0-9-]{20,}'
  'AKIA[0-9A-Z]{16}'
  'AIza[0-9A-Za-z_-]{35}'
)
for pat in "${PATTERNS[@]}"; do
  if git -C "$ROOT" grep -E "$pat" -- ':!*.md' ':!docs/*' 2>/dev/null | grep -v "ejemplo\|example\|MOCK" >/dev/null; then
    err "Patrón sensible detectado: $pat"
    SECRETOS=$((SECRETOS+1))
  fi
done
[ "$SECRETOS" -eq 0 ] && ok "Sin patrones de secretos detectados"

metric secretos_detectados "$SECRETOS"

# .env tracked?
if git -C "$ROOT" ls-files 2>/dev/null | grep -E "^\.env$|^\.env\.production" > /dev/null; then
  err ".env tracked en git — NUNCA commitear"
else
  ok ".env no está en git"
fi

# ─────────────────────────────────────────────────────────────
# 5. Lint y JSON
# ─────────────────────────────────────────────────────────────
section "Lint + JSON"

LINT_FAIL=$(bash "$ROOT/scripts/lint-skills.sh" 2>&1 | tail -3 | grep -oE "Fallidos: *[0-9]+" | grep -oE "[0-9]+" || echo "0")
if [ "$LINT_FAIL" = "0" ]; then ok "Lint SKILL.md: 0 fallos"
else err "Lint SKILL.md: $LINT_FAIL fallos"; fi

JSON_FAIL=0
# Seguridad: pasar $f como argv (NO interpolar en código Python) — previene injection
# si un path llega a contener comillas o caracteres especiales.
while IFS= read -r f; do
  if ! python3 -c 'import json,sys; json.load(open(sys.argv[1]))' "$f" 2>/dev/null; then
    err "JSON inválido: $(echo "$f" | sed "s|$ROOT/||")"
    JSON_FAIL=$((JSON_FAIL+1))
  fi
done < <(find "$ROOT" -name "*.json" -not -path "*/node_modules/*" -not -path "*/__pycache__/*" -not -path "*/.venv/*" -not -path "*/.git/*" 2>/dev/null)
[ "$JSON_FAIL" -eq 0 ] && ok "Todos los .json válidos"

metric lint_fails "$LINT_FAIL"
metric json_fails "$JSON_FAIL"

# ─────────────────────────────────────────────────────────────
# 6. Tests Python MCP (--quick lo salta)
# ─────────────────────────────────────────────────────────────
if [ "$MODE" != "--quick" ] && [ "$MODE" != "--json" ]; then
  section "Tests Python MCP"
  if [ -d "$ROOT/mcp-servers/.venv" ]; then
    PYTEST_OUTPUT=$(cd "$ROOT/mcp-servers" && .venv/bin/python -m pytest -q --no-header 2>&1 | tail -5)
    PASSED=$(echo "$PYTEST_OUTPUT" | grep -oE "[0-9]+ passed" | grep -oE "[0-9]+" || echo "0")
    FAILED=$(echo "$PYTEST_OUTPUT" | grep -oE "[0-9]+ failed" | grep -oE "[0-9]+" || echo "0")
    if [ "$FAILED" = "0" ]; then ok "Tests MCP: $PASSED pasados, 0 fallidos"
    else err "Tests MCP: $PASSED pasados, $FAILED fallidos"; fi
    metric tests_passed "$PASSED"
    metric tests_failed "$FAILED"
  else
    warn "venv mcp-servers no inicializado (cd mcp-servers && python -m venv .venv && .venv/bin/pip install -e .[dev])"
  fi
fi

# ─────────────────────────────────────────────────────────────
# 7. Vencimientos en archivos (e.firma metadata local si existe)
# ─────────────────────────────────────────────────────────────
section "Vencimientos"

if [ -n "${SAT_EFIRMA_CERT:-}" ] && [ -f "${SAT_EFIRMA_CERT:-}" ]; then
  DAYS_LEFT=$(python3 - <<'PYEOF' 2>/dev/null || echo "-1"
import os, sys
try:
    from cryptography import x509
    from cryptography.hazmat.backends import default_backend
    from datetime import datetime, timezone
    with open(os.environ["SAT_EFIRMA_CERT"], "rb") as f:
        data = f.read()
    try:
        cert = x509.load_der_x509_certificate(data, default_backend())
    except Exception:
        cert = x509.load_pem_x509_certificate(data, default_backend())
    days = (cert.not_valid_after_utc - datetime.now(timezone.utc)).days
    print(days)
except Exception:
    print("-1")
PYEOF
  )
  if [ "$DAYS_LEFT" -gt 90 ]; then ok "e.firma vigente: $DAYS_LEFT días restantes"
  elif [ "$DAYS_LEFT" -gt 30 ]; then warn "e.firma vence en $DAYS_LEFT días — agendar renovación"
  elif [ "$DAYS_LEFT" -gt 0 ]; then err "e.firma vence en $DAYS_LEFT días — URGENTE"
  else err "e.firma VENCIDA o no leíble"; fi
  metric efirma_days_left "$DAYS_LEFT"
else
  info "SAT_EFIRMA_CERT no configurado (modo mock OK)"
fi

# ─────────────────────────────────────────────────────────────
# 8. Output final
# ─────────────────────────────────────────────────────────────
if [ "$MODE" = "--json" ]; then
  python3 - "$METRICS_FILE" "$ERRORS" "$WARNINGS" <<'PYEOF'
import json
import sys
metrics_file = sys.argv[1]
errors = int(sys.argv[2])
warnings = int(sys.argv[3])
metrics = {}
with open(metrics_file) as f:
    for line in f:
        line = line.strip()
        if not line or "=" not in line:
            continue
        k, v = line.split("=", 1)
        try:
            metrics[k] = int(v)
        except ValueError:
            metrics[k] = v
metrics['errors'] = errors
metrics['warnings'] = warnings
print(json.dumps(metrics, indent=2, sort_keys=True))
PYEOF
  exit 0
fi

echo ""
echo -e "${BOLD}── Resumen ──${RESET}"
echo "Errores:    $ERRORS"
echo "Warnings:   $WARNINGS"
echo ""
if [ "$ERRORS" -gt 0 ]; then
  echo -e "${RED}❌ Health check con errores${RESET}"
  exit 1
elif [ "$WARNINGS" -gt 0 ]; then
  echo -e "${YELLOW}⚠ Health check con warnings${RESET}"
  exit 0
else
  echo -e "${GREEN}✅ Health check pasó limpio${RESET}"
  exit 0
fi
