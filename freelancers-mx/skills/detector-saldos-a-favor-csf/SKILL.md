---
name: detector-saldos-a-favor-csf
description: Detecta saldos a favor históricos del contribuyente en la Constancia de Situación Fiscal (CSF) o en declaraciones anteriores que NO han sido solicitados al SAT como devolución y aún están dentro del plazo de prescripción (5 años Art. 22 CFF). Genera priorización por monto + edad. Algunos contribuyentes tienen $50k+ MXN sin solicitar durmiendo. Usar cuando el usuario diga saldos a favor olvidados, devolución pendiente sat, dinero del sat que no he reclamado.
allowed-tools: Read, Write
---

# Detector saldos a favor — CSF + declaraciones

## Concepto

Saldo a favor del contribuyente = SAT le debe dinero (típicamente por:
- Retenciones acumuladas mayores al ISR causado
- IVA acreditable mayor al trasladado
- Pagos provisionales mayores al ISR anual

**Prescripción**: 5 años desde que se generó (Art. 22 CFF). Después se pierde.

## Trigger

- "¿tengo dinero del SAT?"
- "saldos a favor olvidados"
- Pre-declaración anual

## Flujo

### 1. Descargar CSF reciente

`mp_sat_portal.sat_descargar_csf(rfc)` — reporta saldos a favor vigentes en padrón.

### 2. Revisar declaraciones anuales últimos 5 años

Por cada ejercicio (`current_year - 5` a `current_year - 1`):
- Buscar resultado declarado: saldo a favor / a pagar
- Si saldo a favor: ¿se solicitó devolución? (sí/no/parcial)

### 3. Output priorizado

```json
{
  "rfc_hash": "...",
  "fecha_consulta": "2026-06-12",
  "saldos_a_favor_detectados": [
    {
      "ejercicio": 2024,
      "monto_mxn": "85000.00",
      "tipo": "ISR_devolucion_no_solicitada",
      "fecha_generacion": "2025-04-30",
      "fecha_prescripcion": "2030-04-30",
      "dias_restantes": 1418,
      "solicitada": false,
      "prioridad": "alta_monto",
      "accion": "Solicitar devolución antes que prescriba"
    },
    {
      "ejercicio": 2021,
      "monto_mxn": "12000.00",
      "tipo": "ISR_devolucion_solicitada_parcial",
      "fecha_solicitud_original": "2022-05-15",
      "fecha_prescripcion": "2027-05-15",
      "dias_restantes": 335,
      "solicitada": true,
      "estado_solicitud": "rechazada_falta_docs",
      "accion": "Reclamar con documentos faltantes ANTES de mayo 2027"
    }
  ],
  "total_potencial_mxn": "97000.00",
  "advertencias": [
    "Solicitudes > $50,000 SAT suele auditar — preparar documentación completa",
    "Rechazos previos pueden ser reclamados con prueba adicional"
  ],
  "vigencia_validada": false
}
```

## Casos edge

| Caso | Acción |
|---|---|
| Cliente cambió RFC (matrimonio) | Saldos previos siguen siendo del titular original — solicitar con RFC anterior |
| Cliente fallecido | Sucesión hereditaria puede reclamar |
| Saldo de PF que ya pasó a PM | Imposible recuperar — son entidades distintas |
| Cliente sin acceso a Buzón | Acudir presencial al SAT |

## Dependencias

- `mp_sat_portal.sat_descargar_csf`
- Tracker local de declaraciones anuales previas

## ⚠ Compliance

- Solicitudes > $50k MXN SAT puede auditar al solicitante (Art. 22-D CFF)
- Documentación rigurosa requerida
- `vigencia_validada: false`
