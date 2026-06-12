---
name: seguimiento-tramites-migratorios
description: Seguimiento status de trámite migratorio en proceso ante INM consultando portal oficial. Muestra etapa actual (recepción, integración, resolución, entrega tarjeta), tiempos estimados, documentos pendientes, opciones si se atrasa. Usar cuando el usuario diga status tramite INM, donde va mi residencia, en que va mi visa.
allowed-tools: Read, Write
---

# Seguimiento trámite migratorio

## Estados INM

| Estado | Descripción | Acción si atorado |
|---|---|---|
| Recibido | INM recibió documentos | Esperar 5-10 días |
| Análisis | Revisión documentación | Esperar 15-30 días |
| Prevención | Pidieron docs adicionales | ⚠ Acudir con docs en plazo (10 días hábiles) |
| Resolución | Se está decidiendo | Esperar 30-90 días |
| Aprobada | Lista para entregar tarjeta | Acudir a recoger en 30 días |
| Negada | Resolución desfavorable | Apelar o re-tramitar |

## Output

```json
{
  "tramite_id": "INM-2026-...",
  "tipo": "residencia_temporal_canje",
  "fecha_solicitud": "2026-03-15",
  "estado_actual": "analisis",
  "dias_en_estado_actual": 65,
  "tiempo_estimado_restante": "15-45 días",
  "documentos_pendientes": [],
  "recomendacion": "Esperar — tiempos normales 60-90d"
}
```
