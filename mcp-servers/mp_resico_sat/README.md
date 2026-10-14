# mp_resico_sat

Régimen Simplificado de Confianza (RESICO) SAT 2026 + retenciones plataformas digitales + alertas expulsión automática.

**Universo**: ~2.5M contribuyentes RESICO + ~1.2M conductores/sellers plataformas.

**Por qué urge**: SCJN 2026 confirmó **expulsión automática sin previo aviso** por 3 omisiones consecutivas o no presentar declaración anual.

## Tools

- `resico_calcular_isr(ingreso_mes_mxn)` — tasa + monto ISR según tramo.
- `resico_evaluar_estatus(rfc, periodos_omitidos, declaracion_anual_presentada, ingresos_anuales_mxn, e_firma_vigente)` — estatus respecto a expulsión + acción recomendada.
- `resico_calendario(anio, mes_actual)` — próximas 12 declaraciones con vencimiento día 17.
- `resico_retencion_plataforma(plataforma, ingreso_bruto_mxn)` — 2.5% estandarizado 2026.
- `resico_solicitar_devolucion(rfc, periodo, monto_solicitado_mxn, plataforma?)` — devolución mes-a-mes 2026.
- `resico_listar_tasas()` — 5 tramos vigentes.
- `resico_listar_plataformas()` — 12 plataformas con retención.

## Estado real (2026-10-14)

No hay upstream: todo es **cálculo local** sobre tablas embebidas en
`shared/resico_sat_mx.py`, por eso las respuestas son `simulated: false`
(antes se marcaban simuladas sin serlo). No se consultó ninguna fuente en vivo.

| Tool | Estado | Nota |
|---|---|---|
| `resico_calcular_isr`, `resico_listar_tasas` | Cálculo local | Tramos 1.00–2.50% y tope $3.5M (Art. 113-E LISR). |
| `resico_retencion_plataforma`, `resico_listar_plataformas` | Cálculo local, **tasa sin verificar** | La "tasa única 2.5% 2026" no está contrastada con fuente primaria (LIF 2026 / DOF); fuentes secundarias se contradicen con el Art. 113-A (1% bienes, 2.1% transporte, 4% hospedaje). La respuesta lo advierte. |
| `resico_evaluar_estatus` | Regla local sobre datos que da el usuario | El criterio "SCJN 2026" no tiene fuente primaria verificada; el Art. 113-I LISR habla de tres o más pagos mensuales omitidos "consecutivos o no", el código solo cuenta un número de omisiones. |
| `resico_calendario` | Cálculo local | Día 17 del mes siguiente. |
| `resico_solicitar_devolucion` | **No se automatiza** (escritura) | Devuelve una referencia `simulated: true`; el folio y la URL no son del SAT. |

El régimen real del contribuyente sale de su Constancia de Situación Fiscal:
`mp_sat_portal.sat_descargar_csf` (e.firma).
