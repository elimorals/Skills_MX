---
name: gestor-efirma-vencimientos
description: Gestiona el ciclo de vida de la e.firma del SAT (Firma Electrónica) para PF o PM. Verifica vigencia leyendo el .cer local (sin necesidad de portal SAT), alerta cuando faltan < 90 días para vencer (las citas en oficinas SAT tardan), guía la renovación (CertiSAT Web si está vigente; SAT ID si es PF y venció hace menos de un año; presencial con cita en los demás casos), y mantiene tracker de e.firmas de múltiples RFCs (caso típico: contador con e.firmas de sus clientes). Usar cuando el usuario diga vigencia efirma, vence mi efirma, renovar firma electronica, gestion efirma. NO usar para firmar documentos (eso es scope de mp_sat_portal).
allowed-tools: Read, Write
---

# Gestor e.firma vencimientos

## Por qué importa

- Sin e.firma vigente no puedes tramitar CSD para facturar, ni hacer trámites que la exigen; varias declaraciones sí aceptan contraseña
- Vigencia: 4 años
- Vías de renovación (fuentes secundarias 2026: ADN40, Milenio, Siempre al Día; confirma en el portal del SAT):
  - **Vigente**: en línea con **CertiSAT Web** (requerimiento .ren generado con la aplicación Certifica), PF y PM
  - **PF vencida hace menos de 1 año**: en línea con **SAT ID**
  - **Vencida hace más de 1 año, PM vencida, o sin archivos/contraseña**: **presencial con cita** (puede tardar semanas)

## Flujo

### 1. Cargar todas las e.firmas del tracker

Para cada RFC con `.cer` registrado:
- Lectura local del `.cer` con `mp_sat_portal/efirma_loader.py` (`EfirmaLoader.metadata()`, campo `days_until_expiry`), o el tool `sat_verificar_efirma_vigente` (MCP `mp_sat_portal`): lee el .cer, comprueba que el .key abre y además intenta el login FIEL; el login con e.firma real está **sin validar en vivo**, así que trata `verificacion_portal` como informativo

### 2. Categorizar

| Días para vencer | Status | Acción |
|---|---|---|
| > 180 | ✅ Verde | Ninguna |
| 91-180 | 🟡 Amarillo | Programar recordatorio |
| 31-90 | 🟠 Naranja | Renovar AHORA en CertiSAT Web |
| 0-30 | 🔴 Rojo | Renovar hoy en CertiSAT Web |
| −365 a −1 | ⛔ Vencida (PF) | SAT ID en línea |
| < −365, o PM vencida | ⛔ Vencida | Cita presencial |

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
      "metodo_renovacion_disponible": "CertiSAT_Web",
      "accion_sugerida": "Renovar en julio 2026 desde casa con Certifica + CertiSAT Web"
    },
    {
      "rfc_hash": "...",
      "tipo": "PM",
      "fecha_vencimiento": "2026-07-01",
      "dias_para_vencer": 19,
      "status": "rojo",
      "metodo_renovacion_disponible": "CertiSAT_Web",
      "accion_sugerida": "RENOVAR ESTA SEMANA en CertiSAT Web: si la e.firma de la PM vence, la renovación es presencial con cita."
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

- `mp_sat_portal/efirma_loader.py` (lectura local) y tool `sat_verificar_efirma_vigente`
- Tracker local de e.firmas

## ⚠ Compliance

- NUNCA loguear path de .key ni password
- e.firma vencida puede impedir renovar el CSD y otros trámites; si por eso una obligación se presenta tarde, hay actualización, recargos y multa
- Guardar e.firmas de clientes requiere autorización expresa de cada titular
