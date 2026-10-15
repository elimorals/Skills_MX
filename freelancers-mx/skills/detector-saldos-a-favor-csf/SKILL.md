---
name: detector-saldos-a-favor-csf
description: Detecta saldos a favor de ISR e IVA en declaraciones anteriores (anuales y mensuales) que NO se han solicitado en devolución ni compensado y siguen dentro del plazo de 5 años (Arts. 22 y 146 CFF). Prioriza por monto y fecha de prescripción. La CSF no muestra saldos a favor: la fuente son los acuses de declaraciones. Usar cuando el usuario diga saldos a favor olvidados, devolución pendiente SAT, dinero del SAT que no he reclamado, tengo saldo a favor de años pasados, recuperar saldo a favor.
allowed-tools: Read, Write
---

# Detector saldos a favor — declaraciones anteriores

## Concepto

Saldo a favor del contribuyente = SAT le debe dinero (típicamente por:
- Retenciones acumuladas mayores al ISR causado
- IVA acreditable mayor al trasladado
- Pagos provisionales mayores al ISR anual

**Prescripción**: la obligación de devolver prescribe en 5 años (Art. 22 penúltimo párrafo y Art. 146 CFF), contados desde que el saldo pudo solicitarse (en la práctica, desde la presentación de la declaración). La solicitud de devolución interrumpe el plazo.

## Trigger

- "¿tengo dinero del SAT?"
- "saldos a favor olvidados"
- Pre-declaración anual

## Flujo

### 1. Reunir acuses de declaraciones

La Constancia de Situación Fiscal **no** muestra saldos a favor (solo régimen, obligaciones y domicilio). Fuentes:
- Acuses y declaraciones de los últimos 5 años que el usuario descargue del portal SAT (Declaraciones → Consultas → Declaraciones presentadas).
- `mp_sat_portal.sat_declaraciones_historico` y `sat_devolucion_estatus` hoy solo devuelven **mock**; con credenciales lanzan `UpstreamError`. No usarlos como fuente real: pedir los acuses al usuario.

### 2. Revisar declaraciones de los últimos 5 años

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
      "fecha_prescripcion": "verificar — la solicitud interrumpió el plazo; recalcular con contador",
      "dias_restantes": null,
      "solicitada": true,
      "estado_solicitud": "rechazada_falta_docs",
      "accion": "Revisar si procede nueva solicitud o medio de defensa contra el rechazo (contador/abogado)"
    }
  ],
  "total_potencial_mxn": "97000.00",
  "advertencias": [
    "El SAT puede verificar la procedencia con facultades de comprobación (Art. 22-D CFF) — preparar CFDI y constancias",
    "Rechazos previos pueden ser reclamados con prueba adicional"
  ],
  "vigencia_validada": false
}
```

## Casos edge

| Caso | Acción |
|---|---|
| Cambio de homoclave o corrección de RFC | El saldo sigue siendo del mismo contribuyente; tramitar con el RFC vigente y aclarar con el SAT |
| Cliente fallecido | Sucesión hereditaria puede reclamar |
| Saldo de PF que ya pasó a PM | Imposible recuperar — son entidades distintas |
| Cliente sin e.firma | La solicitud de devolución requiere e.firma (o contraseña en montos bajos de la anual): tramitarla primero |

## Dependencias

- Acuses de declaraciones proporcionados por el usuario (las tools de histórico del MCP son mock)
- Tracker local de declaraciones anuales previas

## ⚠ Compliance

- El SAT puede revisar la solicitud con facultades de comprobación (Art. 22-D CFF); no hay umbral fijo de monto
- Documentación rigurosa requerida
- `vigencia_validada: false`
