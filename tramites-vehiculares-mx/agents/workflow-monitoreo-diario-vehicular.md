---
name: workflow-monitoreo-diario-vehicular
description: Workflow diario que monitorea status vehicular: revisa multas pendientes en portales municipales (CDMX/EdoMex/MTY), valida verificación próxima, alerta refrendo, y consulta no-circula. Genera reporte de items críticos. Usar cuando el usuario diga monitoreo vehicular, revisa autos, status diario auto.
allowed-tools: Read, Write, Bash
---

# Workflow monitoreo diario vehicular

## Fases

### 1. Cargar tracker placas
`mp_cdmx_municipal`, `mp_edomex_municipal`, `mp_monterrey_municipal` por entidad.

### 2. Multas
Por cada placa: consultar multas pendientes (descontar las ya pagadas hace < 24h).

### 3. Verificación
Validar si está dentro de periodo vigente.

### 4. Refrendo
Si > 1 año desde último refrendo: alerta.

### 5. Hoy no circula
Calendario semanal de qué auto no circula qué día.

### 6. Reporte

```json
{
  "fecha_ejecucion": "2026-06-12",
  "vehiculos_monitoreados": 3,
  "multas_nuevas_detectadas": 1,
  "vehiculos_verificacion_proxima": 1,
  "alertas": [
    "ABC-1234: 1 multa nueva $1,200 (descuento por pronto pago)",
    "XYZ-9876: verificación vence 2026-08-31"
  ]
}
```

## Cron

Diario 08:00 (script `check-multas-vehiculares.sh` ya invoca parte).
