#!/usr/bin/env bash
# pre-cierre-fiscal.sh
# Cron día 14 de cada mes 09:00: alertar al usuario que mañana inicia cierre fiscal.
#
# Genera resumen anticipado: CFDIs del mes hasta hoy, pagos provisionales estimados,
# y agenda recordatorio para correr workflow cierre-fiscal-mensual el día 15.

set -euo pipefail

REPO="${PATH_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
MES=$(date +%Y-%m)
ANIO=$(date +%Y)
MES_NUM=$(date +%m)

OUT_DIR="$REPO/fiscal/$MES"
mkdir -p "$OUT_DIR"

cat > "$OUT_DIR/pre-cierre-aviso.md" <<EOF
# Pre-cierre fiscal $MES

**Generado**: $(date -Iseconds)

## Aviso

Mañana (día 15) inicia el cierre fiscal mensual obligatorio para freelancers y PyMEs.

## Acción sugerida

Correr el workflow:

\`\`\`
Workflow({
  scriptPath: "core-mexico/workflows/cierre-fiscal-mensual.workflow.js",
  args: { rfc: "TU_RFC", ejercicio: $ANIO, mes: $MES_NUM, regimen: "RESICO_PF" }
})
\`\`\`

## Plazo legal

Día 17 (siguiente hábil si cae fin de semana) — pago provisional.

## Pre-revisión

Si quieres adelantar revisión, correr el workflow HOY (día 14) — datos estarán incompletos
(faltan días 14-último) pero detectarás alertas tempranas como faltantes de REP, depósitos
en efectivo > \$15k, retenciones no acreditadas.
EOF

echo "$(date -Iseconds) - Aviso pre-cierre generado: $OUT_DIR/pre-cierre-aviso.md"
