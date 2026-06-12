#!/usr/bin/env bash
# backup-semanal.sh
# Cron viernes 18:00: backup semanal de datos operativos críticos.
#
# Copia a $BACKUP_DIR (configurable):
# - cfdi/ (XMLs + PDFs timbrados)
# - audit-log/ (bitácoras de MCPs)
# - cobranza/ (estado cartera)
# - fiscal/ (cierres mensuales)
# - cartera-seguros/ (si existe)
# - data/ (config usuario)

set -euo pipefail

REPO="${PATH_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
BACKUP_BASE="${PLUGINS_MX_BACKUP_DIR:-$HOME/backups/plugins-mx}"
FECHA=$(date +%Y-%m-%d)
BACKUP_DIR="$BACKUP_BASE/$FECHA"
mkdir -p "$BACKUP_DIR"

# Lista de directorios a respaldar (existan o no)
DIRS=(
  "cfdi"
  "audit-log"
  "cobranza"
  "fiscal"
  "cartera-seguros"
  "data"
  "alertas"
  "dashboards"
)

for d in "${DIRS[@]}"; do
  if [ -d "$REPO/$d" ]; then
    echo "$(date -Iseconds) - Respaldando $d..."
    tar -czf "$BACKUP_DIR/${d}.tar.gz" -C "$REPO" "$d" 2>/dev/null || true
  fi
done

# Cleanup backups > 90 días
find "$BACKUP_BASE" -maxdepth 1 -type d -name "20*" -mtime +90 -exec rm -rf {} \; 2>/dev/null || true

echo "$(date -Iseconds) - Backup semanal completo: $BACKUP_DIR"
ls -lh "$BACKUP_DIR/" 2>/dev/null
