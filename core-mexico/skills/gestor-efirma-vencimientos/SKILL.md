---
name: gestor-efirma-vencimientos
description: Gestiona el ciclo de vida de la e.firma del SAT (Firma Electrónica) para PF o PM. Verifica vigencia leyendo el .cer local (sin necesidad de portal SAT), alerta cuando faltan < 90 días para vencer (no se puede tramitar hoy mismo en oficinas saturadas), guía proceso de renovación anticipada (vía SAT ID en línea si vigente, presencial si vencida o robada), y mantiene tracker de e.firmas de múltiples RFCs (caso típico: contador con e.firmas de sus clientes). Usar cuando el usuario diga vigencia efirma, vence mi efirma, renovar firma electronica, gestion efirma. NO usar para firmar documentos (eso es scope de mp_sat_portal).
allowed-tools: Read, Write
---

# Gestor e.firma vencimientos

## Por qué importa

- Sin e.firma vigente: no puedes presentar declaraciones, descargar CSF, ni operar en línea con SAT
- Renovación presencial requiere cita SAT (puede tardar 30-60 días en zonas saturadas)
- Renovación en línea via SAT ID solo aplica si tu e.firma actual aún está vigente

## Flujo

### 1. Cargar todas las e.firmas del tracker

Para cada RFC con `.cer` registrado:
- Invocar `mp_sat_portal.efirma_loader.EfirmaLoader.metadata()`
- Extraer `days_until_expiry`

### 2. Categorizar

| Días para vencer | Status | Acción |
|---|---|---|
| > 180 | ✅ Verde | Ninguna |
| 91-180 | 🟡 Amarillo | Programar recordatorio |
| 31-90 | 🟠 Naranja | Renovar AHORA via SAT ID |
| 0-30 | 🔴 Rojo | Renovar urgente o cita presencial |
| < 0 | ⛔ Vencida | Solo presencial (no SAT ID) |

### 3. Generar plan de acción

```json
{
  "fecha_corte": "2026-06-12",
  "efirmas": [
    {
      "rfc_hash": "...",
      "nombre_titular_hash": "...",
      "tipo": "PF",
      "fecha_vencimiento": "2026-09-15",
      "dias_para_vencer": 95,
      "status": "amarillo",
      "metodo_renovacion_disponible": "SAT_ID_online",
      "url_sat_id": "https://www.sat.gob.mx/aplicacion/06080/sat-id",
      "accion_sugerida": "Renovar en julio 2026 desde casa"
    },
    {
      "rfc_hash": "...",
      "fecha_vencimiento": "2026-07-01",
      "dias_para_vencer": 20,
      "status": "rojo",
      "metodo_renovacion_disponible": "SAT_ID_online",
      "accion_sugerida": "RENOVAR ESTA SEMANA via SAT ID. Si no, agendar cita presencial."
    }
  ]
}
```

### 4. Cron recomendado

Mensual día 1 09:00:
```
0 9 1 * * bash scripts/check-efirma-vencimientos.sh
```

(Script no incluido en esta entrega — TBD si interesa.)

## Casos edge

| Caso | Acción |
|---|---|
| Múltiples e.firmas (contador con clientes) | Tracker maneja N |
| .cer corrupto / no DER ni PEM | Skill lanza `ValidationError` con mensaje claro |
| e.firma de empresa (PM) | Aplica igual + flag `tipo: "PM"` |
| .cer del titular fallecido | Manejo especial (sucesión) — derivar |

## Dependencias

- `mp_sat_portal.efirma_loader` (ya implementado)
- Tracker local de e.firmas

## ⚠ Compliance

- NUNCA loguear path de .key ni password
- e.firma vencida = no presentación = recargos SAT
