#!/usr/bin/env bash
# backup-semanal.sh
# Cron semanal viernes 18:00 — backup de bitácora + cfdis + cache state.
# Comprime y guarda en ~/backups/plugins-mx/<fecha>.tar.gz
#
# Programar:
#    0 18 * * 5 cd /Users/elias/Documents/Trabajo/skills && bash scripts/backup-semanal.sh >> /tmp/plugins-mx-backup.log 2>&1

set -euo pipefail

SHARE_DIR="${PLUGINS_MX_SHARE_DIR:-$HOME/.local/share/plugins-mx}"
CACHE_DIR="${PLUGINS_MX_CACHE_DIR:-$HOME/.cache/plugins-mx}"
BACKUP_DIR="${PLUGINS_MX_BACKUP_DIR:-$HOME/backups/plugins-mx}"
RETENCION_SEMANAS="${PLUGINS_MX_BACKUP_RETENCION:-12}"

mkdir -p "$BACKUP_DIR"

DATESTAMP=$(date +%Y-%m-%d)
ARCHIVE="$BACKUP_DIR/plugins-mx-$DATESTAMP.tar.gz"

echo "[$(date +%Y-%m-%dT%H:%M:%S)] Backup semanal → $ARCHIVE"

# Backup datos persistentes (excluir cache temporal)
tar -czf "$ARCHIVE" \
    -C "$HOME" \
    "${SHARE_DIR#$HOME/}" 2>/dev/null || {
    echo "  ⚠ Backup falló (puede que no exista share dir aún)"
    exit 0
}

size_kb=$(du -k "$ARCHIVE" 2>/dev/null | cut -f1 || echo 0)
echo "  ✓ Backup creado: ${size_kb}KB"

# Limpiar backups viejos (> retención semanas)
if command -v find >/dev/null 2>&1; then
    deleted=$(find "$BACKUP_DIR" -name "plugins-mx-*.tar.gz" -mtime +$(( RETENCION_SEMANAS * 7 )) 2>/dev/null | wc -l | tr -d ' ')
    if [ "$deleted" -gt 0 ]; then
        find "$BACKUP_DIR" -name "plugins-mx-*.tar.gz" -mtime +$(( RETENCION_SEMANAS * 7 )) -delete 2>/dev/null
        echo "  ✓ Limpiados $deleted backups > $RETENCION_SEMANAS semanas"
    fi
fi

echo "  → Total backups: $(ls $BACKUP_DIR/plugins-mx-*.tar.gz 2>/dev/null | wc -l | tr -d ' ')"
