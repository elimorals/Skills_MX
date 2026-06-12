---
name: seguimiento-devolucion-sat
description: Da seguimiento semanal al status de una devolución de saldo a favor solicitada al SAT, vía consultas al Buzón Tributario (mp_sat_portal). Reporta el avance por etapas (recibida → en revisión → autorizada / rechazada / pendiente información) y alerta cuando el SAT solicita información adicional (deadline corto, 10 días hábiles típicos). Útil entre mayo-julio cuando hay devolución activa. Usar cuando el usuario pregunte estado devolución SAT, donde está mi saldo a favor, status devolución, mi devolución no ha llegado. NO usar para tramitar devolución (eso es manual vía DeclaraSAT).
allowed-tools: Read, Write
---

# Seguimiento devolución SAT

## Cuándo aplica

Después de presentar declaración anual con saldo a favor y haber solicitado la devolución (checkbox en DeclaraSAT). Aplica entre mayo y julio típicamente.

## Trigger

- "¿dónde está mi devolución?"
- "status devolución SAT"
- "mi saldo a favor"
- "han revisado mi declaración?"

## Etapas estándar SAT

| Etapa | Plazo típico | Status |
|---|---|---|
| Recibida | Inmediato | Recibido por SAT, esperando turno |
| En proceso | 10-40 días | SAT revisa cumplimiento de requisitos |
| Pendiente información | Variable | SAT pide info adicional (10 días hábiles) |
| Autorizada | 40-90 días | Aprobada, depósito en proceso |
| Depositada | 1-3 días tras autorización | Saldo cobrado en cuenta CLABE |
| Rechazada | Variable | Negada — analizar motivo |

## Flujo

### Paso 1 — Consultar Buzón Tributario
- Invocar `mp_sat_portal.sat_descargar_buzon_tributario(rfc)`
- Filtrar notificaciones relacionadas con "devolución" / "solicitud" / `ejercicio` del año fiscal

### Paso 2 — Identificar estado
- Buscar palabras clave: "autorizada", "rechazada", "pendiente información", "depositada"
- Si "pendiente información": extraer documentos solicitados y deadline

### Paso 3 — Alertar si urgente
- Pendiente información con deadline < 5 días: ⚠ CRÍTICO
- Sin movimiento > 45 días: 🟡 atender

### Paso 4 — Output

```json
{
  "rfc_hash": "...",
  "ejercicio": 2025,
  "ultima_consulta": "2026-06-12T14:00:00Z",
  "monto_solicitado_mxn": "15000.00",
  "estado": "PENDIENTE_INFORMACION",
  "fecha_solicitud_devolucion": "2026-05-10",
  "fecha_ultima_actualizacion_sat": "2026-06-05",
  "dias_transcurridos": 33,
  "documentos_solicitados": ["estado de cuenta del banco con CLABE confirmada"],
  "deadline_respuesta_sat": "2026-06-20",
  "dias_para_deadline": 8,
  "recomendaciones": [
    "Subir estado de cuenta antes del 20 de junio",
    "Acceder a la opción 'Saldos a favor y devoluciones' en DeclaraSAT"
  ],
  "vigencia_validada": false
}
```

## Casos edge

| Caso | Acción |
|---|---|
| Sin notificaciones en Buzón | Puede ser normal en primeros 30 días — solo informar |
| Rechazo con argumento "discrepancia" | Sugerir invocar `cruzar-bancos-vs-cfdis` para entender |
| Devolución autorizada pero NO depositada > 1 semana | Verificar CLABE registrada en SAT |
| Devolución parcial | SAT autorizó solo parte — analizar motivo |
| Sin acceso al Buzón (sin e.firma) | Pedir al usuario que entre manualmente a https://www.sat.gob.mx |

## Frecuencia recomendada

- Diaria si `dias_para_deadline ≤ 5`
- Semanal entre solicitud y autorización
- Mensual después de depositada (verificar conciliación bancaria)

## Dependencias

- `mp_sat_portal.sat_descargar_buzon_tributario` (mock o real)

## ⚠ Compliance

- Hashear monto y RFC en logs
- `vigencia_validada: false` (status mostrado refleja Buzón, no garantía de pago)
