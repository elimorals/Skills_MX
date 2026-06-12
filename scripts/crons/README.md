# Crons del monorepo plugins-mx

Tareas recurrentes que mantienen frescos los datos del monorepo sin intervención manual.

## Crons disponibles

| Script | Frecuencia | Qué hace |
|---|---|---|
| `refresh-banxico-tcs.sh` | Lun-Vie 10:00 | Descarga TCs DOF de Banxico (USD/EUR/GBP/CAD/JPY) y cachea localmente |
| `refresh-sat-listas-69.sh` | Lun 09:00 | Descarga listas 69 (incumplidos) y 69-B (EFOS) del SAT |

## Instalación

### macOS (launchd)

```bash
# Instalar refresh Banxico
cp scripts/crons/com.plugins-mx.banxico-tcs.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.plugins-mx.banxico-tcs.plist

# Instalar refresh SAT
cp scripts/crons/com.plugins-mx.sat-listas.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.plugins-mx.sat-listas.plist

# Verificar
launchctl list | grep plugins-mx
```

### Linux / WSL (crontab)

```bash
# Ver tu crontab actual
crontab -l

# Hacer backup
crontab -l > /tmp/cron-backup-$(date +%F)

# Cargar el del repo (revisar PATH_REPO en el archivo)
crontab scripts/crons/crontab.linux

# Verificar
crontab -l
```

### Manual (sin cron)

Los scripts también se pueden ejecutar manualmente:

```bash
bash scripts/refresh-banxico-tcs.sh
bash scripts/refresh-sat-listas-69.sh
```

## Logs

| OS | Output | Errores |
|---|---|---|
| macOS | `/tmp/plugins-mx-*.log` | `/tmp/plugins-mx-*.err` |
| Linux | `/tmp/plugins-mx-*.log` | (mezclado vía 2>&1) |

Revisar regularmente:
```bash
tail -50 /tmp/plugins-mx-banxico-tcs.log
tail -50 /tmp/plugins-mx-sat-listas.log
```

## Modo mock

Si los MCPs no tienen credenciales (no hay BANXICO_TOKEN ni SAT_*), los crons corren en mock y **no hacen red**. Útil para entornos de desarrollo sin afectar nada.

Para deshabilitar mock y forzar uso real: definir las env vars en el shell del cron (o en el plist macOS):

```xml
<!-- En el plist -->
<key>EnvironmentVariables</key>
<dict>
    <key>BANXICO_TOKEN</key>
    <string>...tu_token_aqui...</string>
</dict>
```

## Desinstalación

```bash
# macOS
launchctl unload ~/Library/LaunchAgents/com.plugins-mx.banxico-tcs.plist
launchctl unload ~/Library/LaunchAgents/com.plugins-mx.sat-listas.plist
rm ~/Library/LaunchAgents/com.plugins-mx.*.plist

# Linux
crontab -r  # Cuidado: elimina todos tus crons
# o:
crontab -l | grep -v plugins-mx | crontab -
```

## Crons futuros (planeados, no implementados)

- `cierre-fiscal-mensual` día 14 de cada mes — corre `workflow-cierre-fiscal-mensual` (necesita CLI runner)
- `backup-cache-bitacora` diario — respalda `~/.cache/plugins-mx` y `~/.local/share/plugins-mx`
- `cleanup-bitacora-vieja` mensual — borra entradas > 12 meses
- `health-check-mcps` cada 6h — verifica que todos los MCPs responden
