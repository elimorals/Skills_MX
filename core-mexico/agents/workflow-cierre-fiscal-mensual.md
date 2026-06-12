---
name: workflow-cierre-fiscal-mensual
description: Orquesta el cierre fiscal mensual end-to-end (descarga masiva CFDIs emitidos+recibidos del SAT, descarga estado de cuenta bancario, obtiene TCs DOF, cruza ingresos/gastos vs bancos, detecta retenciones sin acreditar, calcula pago provisional ISR/IVA, valida buzón tributario, genera reporte ejecutivo). Despachar cuando el usuario diga "cerrar mes fiscal", "cierre de marzo", "calcula mi pago provisional", "audita el mes pasado", "reporte mensual fiscal", o cron día 14 del mes. Subagent porque coordina 5+ MCPs y procesa cientos de CFDIs.
tools: Read, Write, Bash, Grep
---

# Workflow: Cierre fiscal mensual

Cierra fiscalmente un mes calendario: descarga, cruza, calcula y reporta. Útil para freelancers RESICO/PFAE y PyMEs que necesitan pago provisional sin contador en cada cierre.

## Cuándo te despachan

- Día 14 del mes (cron) — cierre del mes anterior para pago provisional
- Usuario explicito: "cerrar marzo 2026", "reporte fiscal de mes pasado"
- Después de eventos importantes: cambio de régimen, alta nuevo cliente con muchas facturas
- Auditoría retroactiva: revisar un mes específico hacia atrás

## Inputs

```json
{
  "rfc": "MAJG800101XYZ",
  "ejercicio": 2026,
  "mes": 3,
  "regimen": "RESICO_PF" | "PFAE" | "PM_GENERAL",
  "incluir_buzon": true,
  "incluir_aspel": false
}
```

## Fases del workflow

### Fase 1: Recopilación paralela de datos

Las siguientes consultas corren **en paralelo** (no dependen entre sí):

```
parallel([
  () => sat_descargar_cfdi_masivo(rfc, ejercicio, mes, "emitidos"),
  () => sat_descargar_cfdi_masivo(rfc, ejercicio, mes, "recibidos"),
  () => sat_descargar_buzon_tributario(rfc),  // si incluir_buzon=true
  () => banxico_get_tc_dof_mes(ejercicio, mes),  // todos los TCs del mes
  () => banxico_get_uma_anual(ejercicio),
  () => banxico_get_inpc_mes(ejercicio, mes)
])
```

⚠ `sat_descargar_cfdi_masivo` retorna un **solicitud_id** porque el SAT procesa async (1-4 hrs). En modo mock retorna lista sintética inmediata. En modo real:
- Si la solicitud aún no está lista: marcar el cierre como "pendiente_datos" y agendar retry
- Si está lista: descargar ZIP, parsear XMLs internamente

### Fase 2: Cruce ingresos (CFDIs emitidos vs depósitos bancarios)

Si el usuario configuró Aspel/ContPAQi o subió extracto bancario:

```
const ingresos_cfdi = cfdis_emitidos
  .filter(c => c.tipo === "I" && !c.cancelado)
  .reduce((s, c) => s + c.total, 0)

const depositos_banco = aspel_obtener_balanza("102-001-bancos").cargos_del_mes

const diferencia = ingresos_cfdi - depositos_banco
```

Categorías a reportar:
- ✓ **CFDIs cobrados** (match con depósito): pago confirmado
- ⚠ **CFDIs emitidos sin cobro** (PUE/PPD vencido sin depósito): cartera vencida
- 🚨 **Depósitos sin CFDI** (entrada de dinero no facturada): RIESGO — debe facturarse

### Fase 3: Cruce gastos (CFDIs recibidos vs cargos bancarios)

```
const gastos_cfdi = cfdis_recibidos
  .filter(c => c.tipo === "I" && !c.cancelado)
  .reduce((s, c) => s + c.total, 0)

const cargos_banco = aspel_obtener_balanza("102-001-bancos").abonos_del_mes
```

Categorías:
- ✓ **Gastos deducibles** (CFDI a tu RFC + pago bancarizado)
- ⚠ **Gastos en efectivo** (sin pago bancarizado, no deducibles si > $2,000 MXN — Art. 27 LISR)
- 🚨 **Salidas de dinero sin CFDI** (cargos sin factura recibida): pérdida fiscal

### Fase 4: Detección de alertas críticas

Ejecutar en paralelo varios análisis:

1. **Retenciones sin acreditar**: CFDIs recibidos con ISR/IVA retenido que no fueron usados en pago provisional anterior.
2. **Gastos no deducibles**: CFDIs recibidos con UsoCFDI G03 (genérico) pero pagados en efectivo > $2k.
3. **Depósitos en efectivo > $15,000 MXN**: trigger automático para reporte SAT (Art. 32-D).
4. **Multimoneda con TC anómalo**: CFDIs en USD/EUR con TC distinto al DOF del día → diferencia cambiaria.
5. **69-B EFOS** (loop sobre cada RFC emisor de gastos): si alguno aparece, el gasto **NO es deducible** retroactivamente.
6. **Status RFC receptores** de tus ingresos: si alguno cambió a SUSPENDIDO/CANCELADO, alertar.

### Fase 5: Cálculo de pago provisional

Según régimen del usuario:

**RESICO_PF** (más simple):
```
ingresos_efectivamente_cobrados = sum(CFDIs emitidos del mes con MetodoPago=PUE)
                                + sum(REPs emitidos del mes vinculados a PPD viejos)
tasa_resico = ladder({
  $0-$25k → 1.0%,
  $25k-$50k → 1.1%,
  $50k-$83k → 1.5%,
  $83k-$208k → 2.0%,
  $208k-$3.5M → 2.5%
})
isr_a_pagar = ingresos_efectivamente_cobrados × tasa_resico
```

**PFAE** (más complejo):
```
ingresos_acumulados = sum(CFDIs cobrados YTD)
gastos_acumulados = sum(CFDIs deducibles YTD)
utilidad_fiscal = ingresos - gastos - deduccion_personal_proporcional
isr_provisional = aplicar_tarifa_Art_96_LISR(utilidad_fiscal)
                - isr_retenido_acumulado
                - pagos_provisionales_anteriores
```

**IVA**:
```
iva_trasladado = sum(IVA en CFDIs emitidos PUE + REPs del mes)
iva_acreditable = sum(IVA en CFDIs recibidos con UsoCFDI dedutible)
iva_a_pagar = max(0, iva_trasladado - iva_acreditable - iva_retenido_a_acreditar)
```

⚠ Estos cálculos usan tarifas que pueden estar desactualizadas. El workflow reporta `vigencia_validada: false` por default y sugiere consultar contador. Para freelancers RESICO_PF el riesgo es menor (tasas estables). Para PFAE es crítico.

### Fase 6: Verificación con buzón tributario

Si `incluir_buzon=true`:
- Listar notificaciones pendientes
- Marcar urgencias (requerimientos con fecha límite próxima)
- Cruzar con CFDIs del mes (¿algún requerimiento sobre estos?)

### Fase 7: Reporte ejecutivo

Devolver al contexto principal:

```json
{
  "cierre": {
    "rfc_hash": "abc123",
    "periodo": "2026-03",
    "regimen": "RESICO_PF",
    "modo": "real | simulado",
    "vigencia_tarifas_validada": false
  },
  "ingresos": {
    "total_cfdi_emitidos": 250000.00,
    "total_cobrado_en_mes": 220000.00,
    "cartera_vencida_pendiente": 30000.00,
    "depositos_sin_cfdi": 0.00,
    "alerta_facturacion_faltante": false
  },
  "gastos": {
    "total_cfdi_recibidos": 95000.00,
    "deducibles_bancarizados": 85000.00,
    "efectivo_no_deducible": 10000.00,
    "salidas_sin_cfdi": 5000.00,
    "alerta_perdida_fiscal": true
  },
  "pago_provisional": {
    "isr_a_pagar": 4400.00,
    "iva_a_pagar": 12000.00,
    "total_a_pagar": 16400.00,
    "fecha_limite_pago": "2026-04-17",
    "linea_captura_pendiente": true
  },
  "alertas_criticas": [
    "RFC ABC-100101 de un proveedor está en lista 69-B PRESUNTO — $15,000 no son deducibles",
    "Buzón Tributario: requerimiento con fecha límite 2026-04-05",
    "Cliente XYZ tiene 2 CFDIs PPD sin REP — emitir o cancelar"
  ],
  "siguientes_pasos": [
    "Pagar provisional antes del 17 abr 2026 (línea de captura por generar en portal)",
    "Resolver requerimiento Buzón antes del 5 abr",
    "Refacturar provider 69-B o asumir gasto no deducible",
    "Cobrar cartera vencida (despachar /freelancers:cobranza-mensual)"
  ]
}
```

## Manejo de errores

| Caso | Acción |
|---|---|
| Descarga masiva SAT no lista todavía | Marcar `estado_solicitud: pendiente` y agendar retry en 1h |
| RFC del usuario en mock | Reporte completo en modo simulated con datos demo |
| Buzón con requerimiento urgente (<3 días) | **Alerta crítica al inicio del reporte** |
| Depósitos sin CFDI > $50k MXN | **Alerta crítica** — Hacienda puede iniciar revisión |
| Cálculo de pago provisional con tarifas no validadas | Reportar el cálculo + advertir "verificar contador antes de pagar" |
| Aspel no configurado | Skip cruces bancarios. Solo cruce CFDIs entre sí + retenciones |

## Por qué subagent

- Procesa potencialmente cientos de CFDIs (descarga masiva)
- Coordina 5+ MCPs (SAT, Banxico, Banxico CEP, Facturama, Aspel)
- Genera mucho ruido intermedio (cada XML parseado, cada cruce)
- El usuario solo necesita: ingresos cobrados, gastos deducibles, total a pagar, alertas

## Mock-friendly

En modo mock todo el workflow corre con datos demo plausibles:
- Descarga SAT → lista simulada de 3-5 CFDIs por tipo
- Banxico → TCs sintéticos pero con estructura real
- Aspel → datos del mock_data.py (1 mes demo)
- Cálculo de pago provisional → usa tarifas hardcoded marcadas `vigencia: 2026 (no validada)`

Útil para que el usuario vea **el shape del reporte** antes de invertir en conectar credenciales reales.

## Validación pendiente

⚠ Antes de usar para pagar SAT real:
- Validar tarifa Art. 96 LISR 2026 con contador
- Validar tasas RESICO PF 2026 contra portal SAT
- Validar topes Art. 151 deducción personal
- Confirmar deducibilidad de gastos específicos por industria
