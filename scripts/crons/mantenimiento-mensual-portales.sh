#!/bin/bash
# Cron mensual de mantenimiento del catálogo de portales municipales.
#
# Ejecuta secuencialmente:
# 1. Health-check: verifica que las URLs validadas siguen vivas.
# 2. Discovery delta: corre auto-descubrimiento sobre municipios que aún no tienen URL.
# 3. Genera reporte de cambios (qué cayó, qué se descubrió).
# 4. (Opcional) Envía notificación WhatsApp si hay cambios críticos.
#
# Programar en crontab:
#   # Día 5 de cada mes a las 03:00 AM (servidor en hora CDMX)
#   0 3 5 * * /Users/elias/Documents/Trabajo/skills/scripts/crons/mantenimiento-mensual-portales.sh
#
# Setup macOS launchd: ver `scripts/crons/com.plugins-mx.mantenimiento-portales.plist`

set -euo pipefail

# Configuración
REPO_ROOT="${REPO_ROOT:-/Users/elias/Documents/Trabajo/skills}"
SCRIPTS_DIR="$REPO_ROOT/scripts"
MCP_DIR="$REPO_ROOT/mcp-servers"
OUTPUT_DIR="$REPO_ROOT/.cache/mantenimiento-mensual"
FECHA=$(date +%Y-%m-%d)
LOG_FILE="$OUTPUT_DIR/mantenimiento-${FECHA}.log"

mkdir -p "$OUTPUT_DIR"

# Helper: log con timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log "=== Inicio mantenimiento mensual $FECHA ==="
log "REPO_ROOT=$REPO_ROOT"

# ============================================================
# FASE 1: Health-check de URLs validadas actualmente
# ============================================================
log "FASE 1: Health-check de portales validados..."

cd "$MCP_DIR" || { log "ERROR: no se pudo entrar a $MCP_DIR"; exit 1; }

HEALTH_OUTPUT="$OUTPUT_DIR/health-check-${FECHA}.json"
python3 "$SCRIPTS_DIR/health-check-portales.py" \
    --output "$HEALTH_OUTPUT" \
    --timeout 20000 \
    2>&1 | tee -a "$LOG_FILE" || log "⚠ health-check falló — continuando"

if [ -f "$HEALTH_OUTPUT" ]; then
    PORTALES_OK=$(python3 -c "import json; r=json.load(open('$HEALTH_OUTPUT')); print(r['resumen']['portales_cargan'])" 2>/dev/null || echo "?")
    PORTALES_FALLIDOS=$(python3 -c "import json; r=json.load(open('$HEALTH_OUTPUT')); print(r['resumen']['portales_fallidos'])" 2>/dev/null || echo "?")
    log "Health-check: $PORTALES_OK cargan / $PORTALES_FALLIDOS fallidos"
fi

# ============================================================
# FASE 2: Discovery delta — municipios sin URL validada
# ============================================================
log "FASE 2: Discovery sobre municipios pendientes..."

# Generar lista de municipios NO validados aún en el catálogo
PENDIENTES_INPUT="$OUTPUT_DIR/pendientes-${FECHA}.json"
python3 - <<PYEOF
import json
import sys
sys.path.insert(0, "$MCP_DIR")
from shared.catalogo_municipios_mx import MUNICIPIOS

pendientes = []
for estado, muns in MUNICIPIOS.items():
    for clave, mun in muns.items():
        if not mun.validado:
            pendientes.append({
                "estado": estado,
                "mun": clave,
                "nombre": mun.nombre,
            })

with open("$PENDIENTES_INPUT", "w") as f:
    json.dump(pendientes, f, indent=2, ensure_ascii=False)
print(f"Pendientes a investigar: {len(pendientes)}")
PYEOF

DISCOVERY_OUTPUT="$OUTPUT_DIR/discovery-${FECHA}.json"
if [ -s "$PENDIENTES_INPUT" ]; then
    # Skip si llevamos > 2h corriendo (cron debería ser corto)
    timeout 7200 python3 "$SCRIPTS_DIR/descubrir-portal-municipal.py" \
        --input "$PENDIENTES_INPUT" \
        --output "$DISCOVERY_OUTPUT" \
        --workers 3 \
        2>&1 | tee -a "$LOG_FILE" || log "⚠ discovery alcanzó timeout o falló — continuando"
else
    log "Sin pendientes — saltando discovery"
fi

# ============================================================
# FASE 3: Reporte de cambios
# ============================================================
log "FASE 3: Generando reporte..."

REPORTE_MD="$OUTPUT_DIR/reporte-${FECHA}.md"
python3 - <<PYEOF
import json
from pathlib import Path
from datetime import datetime

health_path = Path("$HEALTH_OUTPUT")
discovery_path = Path("$DISCOVERY_OUTPUT")

lineas = [
    f"# Reporte mantenimiento mensual — $FECHA",
    f"",
    f"Ejecutado: {datetime.now().isoformat()}",
    f"",
]

# Health check resumen
if health_path.exists():
    h = json.loads(health_path.read_text())
    lineas.extend([
        "## Health-check de portales validados",
        f"- Evaluados: {h['resumen']['portales_evaluados']}",
        f"- Cargan OK: {h['resumen']['portales_cargan']}",
        f"- Fallidos: {h['resumen']['portales_fallidos']}",
        "",
    ])
    if h['resumen']['portales_fallidos'] > 0:
        lineas.append("### ⚠ Portales que requieren atención:")
        for estado, muns in h.get('resultados', {}).items():
            for mun, datos in muns.items():
                for tipo in ('predial', 'multas'):
                    if tipo in datos and not datos[tipo].get('load_ok'):
                        lineas.append(f"- **{estado}/{mun}** ({tipo}): {datos[tipo].get('error', 'sin info')}")
        lineas.append("")

# Discovery resumen
if discovery_path.exists():
    d = json.loads(discovery_path.read_text())
    estados_count = {}
    for h in d:
        e = h.get('estado_validacion', 'unknown')
        estados_count[e] = estados_count.get(e, 0) + 1
    lineas.extend([
        "## Discovery de pendientes",
        f"- Procesados: {len(d)}",
    ])
    for e, c in sorted(estados_count.items(), key=lambda x: -x[1]):
        lineas.append(f"- {e}: {c}")
    lineas.append("")

    # Nuevos descubiertos
    ok_nuevos = [h for h in d if h.get('estado_validacion') == 'ok']
    if ok_nuevos:
        lineas.append("### ✅ Nuevos municipios descubiertos:")
        for h in ok_nuevos:
            sel = h.get('selectores', {})
            input_sel = (sel.get('input') or ['?'])[0] if sel else '?'
            lineas.append(f"- **{h['estado']}/{h['mun']}**: {h['url_real']} (input: `{input_sel}`)")
        lineas.append("")
        lineas.append("Aplicar al catálogo con: \`python3 /tmp/aplicar-hallazgos.py\`")

# Notas finales
lineas.extend([
    "",
    "## Próximas acciones",
    "1. Revisar portales fallidos arriba — pueden requerir actualizar URL en catálogo",
    "2. Aplicar nuevos hallazgos del discovery al catálogo si los hay",
    "3. Si hay anti-bot nuevo detectado: documentar en `docs/VALIDACION-PORTALES.md`",
])

Path("$REPORTE_MD").write_text("\n".join(lineas))
print(f"Reporte: $REPORTE_MD")
PYEOF

log "Reporte generado: $REPORTE_MD"

# ============================================================
# FASE 4: Notificación opcional (si MP_NOTIFY_WHATSAPP=1)
# ============================================================
if [ "${MP_NOTIFY_WHATSAPP:-0}" = "1" ] && [ -n "${MP_NOTIFY_TEL:-}" ]; then
    log "FASE 4: Notificación WhatsApp..."
    # Comando placeholder — adaptar a tu setup mp_meta_whatsapp
    echo "TODO: enviar reporte via mp_meta_whatsapp a $MP_NOTIFY_TEL"
    log "(Notificación pendiente integración)"
else
    log "FASE 4: Notificación deshabilitada (set MP_NOTIFY_WHATSAPP=1 + MP_NOTIFY_TEL)"
fi

log "=== Mantenimiento mensual completado ==="
log "Output: $OUTPUT_DIR"
log "Reporte: $REPORTE_MD"

# Salida limpia
exit 0
