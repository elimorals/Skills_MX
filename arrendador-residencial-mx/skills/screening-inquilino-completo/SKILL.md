---
name: screening-inquilino-completo
description: Pipeline completo de evaluación de un inquilino candidato para arrendamiento residencial en México. Cubre captura de datos básicos, validación RFC en padrón SAT, consulta a Buró de Crédito Personal (CON AUTORIZACIÓN EXPRESA del candidato — Art. 28 LRSIC), verificación de ingresos vs renta solicitada (idealmente 3x), validación de referencias (2-3 personales o laborales), y generación de recomendación de decisión (Aprobado / Aprobado con depósito mayor / Rechazado). Usar cuando el usuario diga evalúa este inquilino, screening, validar candidato renta, buro inquilino. NO usar sin autorización formal firmada del candidato (consultar buró sin autorización viola la LRSIC y la LFPDPPP).
allowed-tools: Read, Write
---

# Screening inquilino — pipeline completo

## ⚠ COMPLIANCE CRÍTICO

**Consultar Buró de Crédito sin autorización expresa del titular está prohibido** (Art. 28 LRSIC exige autorización expresa y por escrito o medio electrónico; el uso indebido de datos se sanciona además por la LFPDPPP 2025). No afirmes penas concretas sin revisar la ley vigente.

Este skill **NO ejecuta** consulta de Buró sin un `autorizacion_token` válido. El token se obtiene cuando el candidato firma físicamente o electrónicamente una autorización con:
- Nombre completo + CURP
- Fecha + firma autógrafa o electrónica
- Texto de consentimiento explícito ("autorizo consulta a Buró...")
- Vigencia (máx 1 año)

El MCP `mp_buro_credito_personal` valida este token como `autorizacion_token: str = Field(..., min_length=16)` a nivel schema.

## Pipeline

### Paso 1 — Captura datos básicos

Pedir al usuario (operador, no candidato directo):

```json
{
  "nombre_completo": "Juan Pérez García",
  "rfc": "PEGJ900101ABC",
  "curp": "PEGJ900101HDFRRN01",
  "tel": "+5215551234567",
  "email": "j.perez@example.com",
  "ingreso_mensual_declarado_mxn": "30000",
  "renta_solicitada_mxn": "12000",
  "referencias": [
    {"tipo": "laboral", "nombre": "...", "tel": "..."},
    {"tipo": "personal", "nombre": "...", "tel": "..."}
  ]
}
```

### Paso 2 — Validación RFC en padrón SAT

Invocar `sat_consultar_padron` (MCP `mp_sat_portal`; requiere e.firma y no está validado — si falla, pide la constancia de situación fiscal del candidato):
- Si RFC no existe en padrón: 🔴 alerta crítica
- Si estado "Suspendido": 🟡 alerta
- Si estado "Activo": ✅ continuar

### Paso 3 — Validación 69-B

Invocar `sat_consultar_69b_efos` (validado en vivo):
- Si en lista definitiva: 🔴 RECHAZAR de inmediato
- Si en presuntos: 🟡 alertar, evaluar contexto

### Paso 4 — Buró (con autorización)

⚠ Antes de invocar:
1. Confirmar con operador que tiene autorización firmada por el candidato
2. Pedir `autorizacion_token` (string >= 16 chars que representa el hash de la autorización física/electrónica)
3. Si falta token: ABORTAR con mensaje claro de compliance

Invocar `buro_consultar_score` / `buro_descargar_reporte_completo` (MCP `mp_buro_credito_personal`, estado: sin verificar / mock). Si devuelve datos mock, NO los uses para decidir: pide al candidato su Reporte de Crédito Especial (gratuito una vez al año en burodecredito.com.mx). Criterios:
- Score > 650: ✅ apto
- Score 550-650: 🟡 apto con depósito mayor
- Score < 550: 🟡 evaluar con cuidado
- Sin historial: depende de antigüedad RFC (revisar caso por caso)

### Paso 5 — Verificación de ingresos

Regla del 3x: ingreso mensual del candidato debe ser >= 3x la renta.
- $30,000 / $12,000 = 2.5x → 🟡 menor a regla, pero OK con aval o depósito mayor
- $36,000 / $12,000 = 3.0x → ✅
- $50,000 / $12,000 = 4.2x → ✅✅

Cómo verificar:
- Pedir 3 últimos recibos de nómina (asalariado)
- Pedir 3 últimos estados de cuenta (freelancer / negocio)
- Pedir 3 últimos CFDIs de honorarios (freelancer formal)

### Paso 6 — Validación de referencias

Pidir al menos:
- 1 referencia laboral (jefe directo / RH)
- 1 referencia personal (no familiar directo)
- Idealmente 1 referencia de arrendamiento previo

Llamar (operador) y validar:
- Existe la persona
- Conoce al candidato hace > 6 meses
- Opinión cualitativa (puntualidad, cuidado, etc.)

### Paso 7 — Recomendación

```python
def decidir(score: int, ingreso_ratio: float, hay_alertas_sat: bool, ref_ok: int) -> str:
    if hay_alertas_sat or ref_ok < 2:
        return "RECHAZADO"
    if score >= 650 and ingreso_ratio >= 3.0:
        return "APROBADO"
    if score >= 550 and ingreso_ratio >= 3.0:
        return "APROBADO_CON_AVAL"            # buen ingreso, buró regular
    if score >= 550 and ingreso_ratio >= 2.5:
        return "APROBADO_CON_DEPOSITO_MAYOR"  # ej. 2 meses de depósito
    return "RECHAZADO"

assert decidir(720, 3.0, False, 2) == "APROBADO"
assert decidir(600, 3.2, False, 2) == "APROBADO_CON_AVAL"
assert decidir(600, 2.5, False, 2) == "APROBADO_CON_DEPOSITO_MAYOR"
```

## Output

```json
{
  "operation": "screening_inquilino",
  "candidato_id_hash": "...",
  "rfc_hash": "...",
  "fecha_screening": "2026-06-12",
  "datos_basicos_completos": true,
  "rfc_padron_sat": "ACTIVO",
  "alerta_69b": null,
  "buro": {
    "consultado": true,
    "score": 720,
    "rango": "BUENO_ALTO"
  },
  "ingreso_mensual_mxn": "36000.00",
  "renta_solicitada_mxn": "12000.00",
  "ratio_ingreso_renta": 3.0,
  "referencias_validadas": 2,
  "decision_recomendada": "APROBADO",
  "deposito_sugerido_mxn": "12000.00",
  "advertencias": [],
  "vigencia_validada": false
}
```

## Casos edge

| Caso | Acción |
|---|---|
| Sin autorización Buró firmada | ABORTAR — explicar compliance |
| Candidato extranjero sin RFC mexicano | Aceptable si tiene pasaporte + visa vigente — score basado en ingresos + referencias |
| Score = "sin historial" pero ingreso 5x | APROBADO con dep estándar (probablemente joven sin créditos) |
| Inquilino paga renta upfront 6 meses | Aplica solo si caso especial — documentar bien |
| Familiar directo del arrendador | Decisión personal del dueño, sin compliance crítico |

## Dependencias

- `mp_sat_portal` (padrón + 69-B)
- `mp_buro_credito_personal` (con autorización formal)
- Tracker local de candidatos

## ⚠ Privacy

- RFC, CURP, score Buró: **NUNCA loguear en claro**
- Resultados se guardan cifrados o hasheados
- Datos del candidato rechazado: borrar cuando ya no sean necesarios para la finalidad (política sugerida: 6 meses), conforme al aviso de privacidad
