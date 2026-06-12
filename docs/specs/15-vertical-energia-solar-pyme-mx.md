---
spec: "vertical-energia-solar-pyme-mx"
estado: "DRAFT"
creado: "2026-06-12"
autor: "Elias"
ultima_actualizacion: "2026-06-12"
esfuerzo_estimado_horas: [250, 420]
prioridad: "tier-2"
---

# Spec 15 — Vertical `energia-solar-pyme-mx`

## 1. Propósito

Plugin para **PYMES y comercios mexicanos con consumo eléctrico medio-alto** (tarifa GDMTH o PDBT con demanda > 25 kW) que tienen o evalúan **paneles solares con interconexión a la red CFE**. Mercado: ~85k negocios con sistema instalado y crecimiento ~30%/año.

Resuelve:
1. Lectura de medidor bidireccional CFE (energía consumida vs energía inyectada)
2. Cálculo del **crédito en kWh** acumulado (CFE no paga efectivo, solo créditos en próxima factura)
3. Validación de la facturación CFE bimestral / mensual (errores comunes ~15%)
4. Compliance interconexión NOM-001-SEDE-2018 (instalación) + NOM-001-SEDE-2026 (vigencia)
5. Tracking ROI del sistema (cuándo se paga vs cuánto ahorra/mes)

## 2. Contexto y por qué es novedoso

- **No hay vertical de energía**: ningún plugin actual toca CFE / facturas / interconexión
- **Tarifas GDMTH (Mediano Tensión Hora)**: la más común para PyME con demanda > 25 kW; tres horarios:
  - Punta (1h-4h pm): tarifa más alta
  - Intermedia (resto): intermedia
  - Base (madrugada): más baja
- **Medidor bidireccional**: instalado por CFE cuando interconectas paneles solares; mide en ambas direcciones
- **Modalidades de interconexión CFE**:
  - Net Metering (pequeño escala, < 0.5 MW): crédito kWh, neto = consumido - inyectado
  - Net Billing (gran escala): pago monetario por kWh inyectado
  - Venta total: 100% al mercado mayorista (no para PyME típica)
- **Reformas 2024-2026**: ya no nuevos contratos net metering para industriales — solo net billing
- **NOM-001-SEDE**: estándar técnico obligatorio; CFE verifica al instalar

## 3. Alcance

**Dentro:**
- Lectura factura CFE bidireccional (parse de PDF)
- Cálculo crédito kWh acumulado por periodo
- Validación factura vs medidor (detección errores CFE típicos)
- Tracking generación solar vs consumo (si hay datos de inversor)
- ROI calculator (payback del sistema solar)
- Calendario tarifa GDMTH (punta/intermedia/base horarios)
- Recomendación optimización (cargar baterías en base, descargar en punta)
- Alertas: factor de potencia bajo, sobrefacturación detectada
- Tracking compliance contrato interconexión

**Fuera (decisión deliberada):**
- Diseño técnico del sistema solar (eso es ingeniero)
- Instalación física (eso es instalador)
- Venta a mercado mayorista (escala industrial)
- Otras formas de generación (eólica, gas, biomasa)
- Tarifas residenciales (DAC, 1A-1F) — PyME GDMTH only
- Sistemas off-grid (sin interconexión CFE)

## 4. Inputs / outputs / schemas

### Cuenta CFE

```python
class CuentaCFE(BaseModel):
    rpu: str                          # Registro Permanente del Usuario (número de cuenta CFE)
    tarifa: Literal["GDMTH", "GDMTO", "PDBT", "DAC", "GDBT", "G_T"]
    rfc: str
    razon_social: str
    direccion_servicio: str
    interconectado_solar: bool
    contrato_interconexion: str | None
    fecha_alta_contrato_interconexion: date | None
    capacidad_instalada_kw: Decimal | None
    modalidad: Literal["net_metering", "net_billing"] | None
```

### Factura CFE

```python
class FacturaCFE(BaseModel):
    rpu: str
    periodo_facturacion: tuple[date, date]
    energia_consumida_kwh: Decimal
    energia_inyectada_kwh: Decimal  # si interconectado
    energia_neta_kwh: Decimal       # consumido - inyectado
    credito_kwh_acumulado_inicio: Decimal
    credito_kwh_acumulado_fin: Decimal
    desglose_horarios: dict[Literal["punta", "intermedia", "base"], Decimal]  # solo GDMTH
    factor_potencia: Decimal | None
    cargo_demanda_kw: Decimal | None  # solo GDMTH
    iva_16_mxn: Decimal
    dap_mxn: Decimal                 # Derecho de Alumbrado Público (municipal)
    total_mxn: Decimal
    proximo_pago_fecha: date
```

## 5. Skills propuestos (9)

| Skill | Cuándo activa |
|---|---|
| `lectura-factura-cfe-pdf` | Parser PDF mensual/bimestral |
| `validacion-factura-cfe` | Detección errores comunes |
| `credito-kwh-tracking` | Acumulado por mes |
| `roi-solar-payback` | Cálculo recuperación inversión |
| `dashboard-energia-mensual` | Status integral |
| `optimizacion-tarifa-gdmth` | Recomendaciones horario |
| `factor-potencia-monitoreo` | Alerta si < 0.9 (penalización CFE) |
| `comparador-net-metering-vs-billing` | Para decidir contrato |
| `compliance-interconexion-nom001` | Status contrato |

## 6. Comandos (5)

```
/solar:dashboard
/solar:factura
/solar:roi
/solar:optimizacion-horario
/solar:credito-kwh
```

## 7. Workflow

`workflow-cierre-mensual-energia.md`:
1. Cargar factura CFE del mes (PDF)
2. Parsear datos + validar vs mes pasado
3. Detectar anomalías: factor potencia bajo, cobro DAP duplicado, etc.
4. Actualizar credito kWh acumulado
5. Generar dashboard del mes
6. Calcular ahorro mensual vs sin solar
7. Actualizar ROI cumulativo (payback period restante)

## 8. Casos edge

| Caso | Acción |
|---|---|
| Mes con generación > consumo | CFE NO paga efectivo — solo créditos kWh acumulan |
| Cliente cambió tarifa mid-año (GDMTH a PDBT) | Recalcular por periodo |
| Sistema solar quitado o no funcionando | Factura volverá a "normal" (sin inyección) |
| Sobrefacturación detectada | Reclamar a CFE con evidencia + plazo 30 días |
| Crédito kWh > consumo año | Acumula sin pago efectivo — sugerir aumentar consumo o vender |
| Cambio de modalidad net metering → billing | Crédito existente convertir a monetario |
| Factor potencia < 0.9 | Multa CFE — sugerir banco capacitores |
| Falta de datos del inversor solar | Solo trabajar con datos CFE |

## 9. Dependencias

- **MCPs**: `mp_facturama_extendido` (CFDI gastos energía deducibles), `mp_banxico` (INPC para ROI inflación)
- **MCPs nuevos sugeridos**: `mp_cfe_factura_parser` (parse PDF oficial CFE), `mp_inversor_solar_modbus` (para datos de inversor — varía por marca)
- **Skills `_shared/`**: cfdi-emision, mxn-formato

## 10. Criterios de aceptación

- [ ] Plugin completo
- [ ] Parser PDF factura CFE funciona para PDFs oficiales 2024-2026
- [ ] Cálculo crédito kWh correcto contra factura
- [ ] Detección de 5+ tipos de error de facturación comunes
- [ ] ROI calculator con asunciones explícitas (inflación + crecimiento tarifa)
- [ ] Dashboard claro y útil
- [ ] Tests con 5 fixtures (factura normal, con crédito, GDMTH, sobrefacturación, PDBT)
- [ ] Lint passing

## 11. Esfuerzo estimado

- **Scaffold**: 5-10h
- **9 skills**: 90-150h
- **Parser PDF factura CFE**: 40-60h (variabilidad de PDFs)
- **Validación + detección errores**: 30-50h
- **ROI calculator con asunciones**: 25-40h
- **Calendario tarifa GDMTH**: 15-25h
- **Tests + 5 fixtures**: 25-40h
- **Docs + guía**: 20-30h
- **Validación con instalador solar / electricista certificado**: 5-10h coordinación
- **TOTAL**: **250-415 horas** (~6-10 semanas FT)

## 12. Riesgos + mitigaciones

| Riesgo | Prob | Impacto | Mitigación |
|---|---|---|---|
| CFE cambia formato factura | Media | Alto | Parser modular + tests con muestras vigentes |
| Tarifas GDMTH cambian | **Alta (anual)** | Alto | Catálogo separado + revisión enero |
| Net metering reformado (ya pasó parcial 2024) | Alta | Alto | Soportar net billing también |
| Datos del inversor solar no estándar | Alta | Medio | Trabajar solo con datos CFE como fallback |
| Cliente cambia de tarifa mid-año | Media | Bajo | Calcular por periodo |

## 13. Decisiones pendientes

- [ ] ¿Producto B2B comercializador (instaladores solares lo venden a clientes) o B2C directo?
- [ ] ¿Integración con principales fabricantes inversores (Solis, Growatt, Huawei, SMA)?
- [ ] ¿Soporte tarifa DAC residencial (caso edge)?
- [ ] ¿Pricing: $499 MXN/mes por sistema o flat por cliente?

## 14. Plan de implementación

### Fase 1: Scaffold + catálogo tarifas (20-30h)
### Fase 2: Parser PDF factura CFE (40-60h)
### Fase 3: Skills crédito kWh + tracking (40-60h)
### Fase 4: ROI calculator + dashboard (35-55h)
### Fase 5: Validación + detección errores (30-50h)
### Fase 6: Optimización + factor potencia (30-50h)
### Fase 7: Tests + docs (55-100h)

## 15. Links

- [Sunwise - Tarifa GDMTH y GDMTO 2026](https://blog.sunwise.io/tarifas-gdmto-y-gdmto/)
- [SolarPanelCancun - Medidor bidireccional CFE](https://www.solarpanelcancun.com/blog/medidor-bidireccional-cfe-como-funciona)
- [SILYMX - Energía solar México 2026 fiscal](https://sily.mx/blogs/base-de-conocimientos-noticias/energia-solar-en-mexico-2026-beneficios-fiscales-costos-e-interconexion-cfe)
- [Leasol - CFE y paneles solares net metering](https://leasol.com.mx/cfe-y-paneles-solares-en-empresas-guia-completa-de-interconexion-y-medicion-en-mexico/)
- [Revolgética - Interconexión CFE paneles industriales](https://revolgetica.com/interconexion-cfe-paneles-solares-industriales-mexico/)
- [Energy Magazine - Tarifas GDMTH 2026](https://energymagazine.mx/2026/01/analisis-tarifas-2026-asi-cambian-tus-costos-si-eres-gdmth-y-que-mirar-en-tus-clausulas-de-suministro/)
- [Marsam Solar - Tarifa GDMTH](https://marsamsolar.com/tarifa-gdmth-que-es-como-se-cobra-y-como-influye-en-tu-empresa/)
- [CFE - Tarifa GDMTH oficial](https://app.cfe.mx/Aplicaciones/CCFE/Tarifas/TarifasCRENegocio/Tarifas/GranDemandaMTH.aspx)
