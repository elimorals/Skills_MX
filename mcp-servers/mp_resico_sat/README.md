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
