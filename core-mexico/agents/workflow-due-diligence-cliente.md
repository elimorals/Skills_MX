---
name: workflow-due-diligence-cliente
description: Orquesta due-diligence completa de un cliente nuevo (PF o PM) antes de aceptarlo en cartera. Coordina validación RFC, status SAT padrón, lista 69-B EFOS, lista 69 incumplidos, descarga CSF, screening Buró (con autorización), validación de dirección, score de riesgo final 1-100. Despachar cuando el usuario diga "due diligence cliente", "valida nuevo cliente", "screening cliente B2B", "antes de aceptar al cliente X", "cliente nuevo grande". Subagent porque coordina 5+ MCPs y consume tokens elevados.
tools: Read, Write, Bash, Grep
---

# Workflow: Due-diligence de cliente nuevo

Antes de aceptar un cliente en cartera (especialmente B2B con monto significativo), validar su salud fiscal y comercial.

## Cuándo te despachan

- Cliente nuevo con factura > $100,000 MXN
- Cliente B2B con quien se firmará contrato anual
- Inquilino potencial > $20,000 MXN/mes de renta
- Proveedor nuevo que vas a usar > $50,000 MXN/mes
- Refinanciamiento o renegociación con cliente existente

## Inputs requeridos

```json
{
  "rfc": "ABC010101AA1",
  "nombre": "Cliente Demo SA de CV",
  "tipo": "PF | PM",
  "monto_operacion_estimado_mxn": 250000,
  "autorizacion_buro_token": "{{token_firma_digital}}"  // si aplica
}
```

## Fases del workflow

### Fase 1: Validación local RFC (instantánea)

```
skill rfc-validacion(rfc) →
  - estructura correcta
  - no es genérico (XAXX, XEXX)
  - sin palabras inconvenientes
  - tipo PF vs PM coherente con length
```

Si falla → abortar inmediatamente, NO continuar.

### Fase 2: Verificaciones SAT en paralelo

```
parallel([
  () => mp_sat_portal.sat_consultar_padron(rfc),
  () => mp_sat_portal.sat_consultar_69b_efos(rfc),
  () => mp_sat_portal.sat_consultar_69_incumplidos(rfc),
  () => mp_sat_portal.sat_descargar_csf(rfc)  // si tienes credenciales
])
```

Análisis por status:

| Status SAT | Score impacto | Acción |
|---|---|---|
| Padrón ACTIVO + sin listas | +30 | Continuar |
| Padrón SUSPENDIDO | -50 | Solicitar regularizar primero |
| Padrón CANCELADO | -100 | NO ACEPTAR |
| Padrón NO_LOCALIZADO | -40 | Investigar dirección |
| 69-B PRESUNTO | -60 | Riesgo deducibilidad — alertar al cliente |
| 69-B DEFINITIVO | -100 | NO ACEPTAR — no se pueden deducir gastos |
| 69 Incumplidos NO_LOCALIZADO | -30 | Riesgo cobranza |
| 69 Incumplidos DOMICILIO_FALSO | -50 | Investigar |

### Fase 3: Buró de Crédito (si aplica + con autorización)

Solo aplicable si:
- Operación con riesgo crediticio (renta, préstamo, financiamiento)
- Tienes autorización formal del cliente

```
si autorizacion_buro_token presente:
  mp_buro_credito_personal.buro_consultar_score(rfc, autorizacion_buro_token)
  mp_buro_credito_personal.buro_descargar_reporte_completo(rfc, autorizacion_buro_token)
```

| Score Buró | Impacto |
|---|---|
| 725+ (excelente) | +20 |
| 650-724 (bueno) | +10 |
| 549-649 (regular) | 0 |
| 450-548 (malo) | -20 |
| < 450 (muy malo) | -40 |

### Fase 4: Validación de dirección

Verificar coherencia entre:
- Dirección declarada por el cliente
- Dirección en CSF (si descargada)
- Geolocalización vía Google Places (futuro)
- Inconsistencias → red flag

### Fase 5: Análisis financiero (si PM)

Buscar:
- Estados financieros públicos (si SEC, BMV)
- Antigüedad de la empresa (alta vs reciente)
- Cantidad de empleados aprox

Si > 50 empleados: empresa grande, riesgo bajo
Si < 5 empleados: micro, riesgo variable, requiere más due-diligence

### Fase 6: Cálculo de score final

```
score_final = 100 + impactos_de_fases_2_a_4
```

Categorías:
- **80-100**: Riesgo BAJO → aceptar normal
- **60-79**: Riesgo MEDIO → aceptar con condiciones (anticipo 50%, garantía)
- **40-59**: Riesgo ALTO → aceptar solo con prepago total o garantía fuerte
- **< 40**: NO ACEPTAR

### Fase 7: Reporte ejecutivo

```json
{
  "due_diligence": {
    "cliente": "Cliente Demo SA de CV",
    "rfc_hash": "abc123",
    "tipo": "PM",
    "fecha_evaluacion": "2026-03-15",
    "score_final": 78,
    "categoria_riesgo": "MEDIO",
    "decision_recomendada": "ACEPTAR_CON_CONDICIONES",
    "fases": {
      "rfc_validacion": "OK",
      "padron_sat": "ACTIVO",
      "69b_efos": "NO_APARECE",
      "69_incumplidos": "NO_APARECE",
      "csf_descargada": true,
      "buro_credito": {
        "consultado": true,
        "score": 685,
        "categoria": "bueno"
      },
      "validacion_direccion": "OK"
    },
    "alertas": [
      "Empresa con < 2 años de operación — riesgo moderado",
      "Padrón muestra obligaciones recientes (IVA + ISR) — al corriente"
    ],
    "condiciones_sugeridas": [
      "Anticipo 50% antes de servicio",
      "Contrato con cláusula de cancelación al primer impago",
      "Revisión semestral del estado fiscal"
    ],
    "siguientes_pasos": [
      "Enviar contrato a firma con condiciones",
      "Agendar revisión D+180 días"
    ]
  }
}
```

## Manejo de errores

| Caso | Acción |
|---|---|
| RFC en 69-B DEFINITIVO | Abortar inmediatamente. NO aceptar. |
| Buró score < 450 | Recomendar NO aceptar. Si insisten, requerir garantía solidaria. |
| Cliente niega autorización Buró | Procesar sin Buró, score más bajo. |
| Sin credenciales SAT (mock mode) | Reporte con datos demo, marcar `simulated: true`. |
| Cliente con CSF rechazada por SAT | Solicitar al cliente regularizar. |

## Por qué subagent

- 5+ MCPs consultados
- Genera ~3-5KB de datos intermedios por verificación
- El usuario solo necesita: score + decisión + condiciones

## Mock-friendly

Sin credenciales reales todo corre en mock:
- SAT padrón: ACTIVO siempre
- 69-B/69: lista demo de 2-3 RFCs presuntos
- Buró: requiere token de autorización válido
- CSF: estructura plausible con `simulated: true`
