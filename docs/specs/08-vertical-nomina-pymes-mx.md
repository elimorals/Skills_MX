---
spec: "vertical-nomina-pymes-mx"
estado: "DRAFT"
creado: "2026-06-12"
autor: "Elias"
ultima_actualizacion: "2026-06-12"
esfuerzo_estimado_horas: [400, 650]
prioridad: "tier-1"
---

# Spec 08 — Vertical `nomina-pymes-mx`

## 1. Propósito

Plugin para PyMEs mexicanas con 1-50 empleados que pagan **sueldos régimen 605**. Mercado: ~600k PyMEs registradas con empleados (INEGI ENOE 2024).

Resuelve el **dolor crítico** del patrón pequeño: emitir CFDI Nómina 4.0 con Complemento 1.2 (obligatorio, Art. 99 LISR, NO admite excepción), cumplir con altas/bajas/modificaciones SUA-IDSE ante IMSS dentro de los plazos legales, calcular retenciones ISR + IMSS + INFONAVIT + Subsidio empleo correctamente, y entregar recibos a empleados.

**Por qué importa**: errar en CFDI Nómina o IMSS-IDSE = multas SAT + capitales constitutivos IMSS que pueden quebrar al patrón pequeño.

## 2. Contexto y por qué es novedoso

- **No hay vertical de nómina en repo**: `freelancers-mx` cubre PF que factura, no PF que paga sueldos a otros
- **CFDI Nómina 4.0 + Complemento 1.2 Revisión E**: vigente desde 29 dic 2025; obligatorio cada quincena/mes
- **IMSS-IDSE + SUA**: SUA es software desktop obligatorio del IMSS para altas/bajas/modificaciones; integración por archivo .SUA
- **Subsidio para el empleo**: tarifa específica (no Art. 96 LISR estándar) — se aplica si sueldo bruto < tope mensual UMA
- **Cierre fiscal mensual de nómina**: incluido en `core-mexico/cierre-fiscal-mensual` pero parcialmente — falta la parte SUA

## 3. Alcance

**Dentro:**
- Captura empleados (alta IMSS + alta nómina interna)
- CFDI Nómina 4.0 + Complemento 1.2 Rev. E quincenal/mensual
- Cálculo ISR salarios (Art. 96 LISR tarifa salario + subsidio empleo)
- Cuotas IMSS obrero-patronales (SBC + factor de integración)
- Cuotas INFONAVIT 5% + descuentos crédito si aplica
- Generación archivo SUA para envío IDSE
- Bajas/modificaciones IDSE (cambio sueldo, ausentismos, incapacidades IMSS)
- Recibo PDF al empleado
- Aguinaldos (15 días mínimo Art. 87 LFT)
- PTU (10% utilidad fiscal Art. 117 LFT)
- Vacaciones (12 días año uno, +2/año hasta 32, ajuste 2023 LFT)

**Fuera (decisión deliberada):**
- PyMEs > 50 empleados (otra escala — sistemas como Aspel NOI o SAP)
- Nóminas con sindicato (negociación CCT — fuera de scope)
- Asimilados a salarios (caso edge)
- Empleados extranjeros (visados + retenciones especiales)
- Liquidaciones / finiquitos litigiosos (requiere abogado laboral)

## 4. Inputs / outputs / schemas

### Empleado

```python
class Empleado(BaseModel):
    rfc: str
    curp: str
    nss: str  # Número Seguridad Social IMSS (11 dígitos)
    nombre_completo: str
    fecha_alta: date
    fecha_baja: date | None
    puesto: str
    departamento: str | None
    regimen_contratacion: Literal["02_sueldos", "08_indemnizacion"]
    tipo_contrato: Literal["01_indefinido", "02_obra_determinada", "03_tiempo_determinado"]
    sueldo_diario_mxn: Decimal       # base sin prestaciones
    sueldo_diario_integrado_mxn: Decimal  # SBC con factor 1.0452 mínimo
    periodicidad_pago: Literal["02_quincenal", "04_mensual"]
    cuenta_clabe_pago: str
    aplica_credito_infonavit: bool
    monto_credito_infonavit_mxn: Decimal | None
    aplica_alimentaria: bool
    monto_alimentaria_mxn: Decimal | None
```

### CFDI Nómina output

```python
class CfdiNominaResult(BaseModel):
    uuid: str
    empleado_rfc_hash: str
    periodo_inicio: date
    periodo_fin: date
    sueldo_bruto: Decimal
    isr_retenido: Decimal
    subsidio_empleo_aplicado: Decimal
    imss_obrero_retenido: Decimal
    infonavit_descontado: Decimal | None
    otros_descuentos: list[Descuento]
    neto_pagar: Decimal
    xml_path: Path
    pdf_path: Path
    forma_pago: str  # 03 transferencia, 01 efectivo (no recomendado)
    vigencia_validada: bool
```

## 5. Skills propuestos (10)

| Skill | Cuándo activa |
|---|---|
| `dashboard-nomina-quincenal` | Resumen quincenal |
| `alta-empleado-completa` | Onboarding (RFC + NSS + datos) |
| `baja-empleado-imss` | Off-boarding |
| `calculo-isr-salarios-art96` | Cálculo ISR + subsidio empleo |
| `cuotas-imss-sbc` | IMSS obrero + patronal por empleado |
| `cuotas-infonavit-5pct` | INFONAVIT por empleado |
| `cfdi-nomina-quincenal` | Emisión + timbrado |
| `aguinaldo-y-ptu-anual` | Cálculos anuales |
| `vacaciones-prima-vacacional` | Días + prima 25% |
| `sua-idse-export` | Generar archivo .SUA |

## 6. Comandos (6)

```
/nomina:dashboard
/nomina:alta-empleado
/nomina:correr-nomina
/nomina:cfdi-mes
/nomina:aguinaldo
/nomina:sua-export
```

## 7. Workflow

`workflow-corrida-nomina-quincenal.md` — orquestador end-to-end:
1. Cargar empleados activos del periodo
2. Por cada uno: sueldo + ausentismos + incapacidades + extras
3. Calcular ISR + IMSS + INFONAVIT
4. Aplicar descuentos (alimentaria, otros)
5. Calcular neto a pagar
6. Emitir CFDI Nómina (timbrado)
7. Generar archivo dispersión SPEI por banco
8. Generar archivo SUA para IDSE
9. Enviar recibo a cada empleado (email/WhatsApp)
10. Persistir + reportar discrepancias

## 8. Casos edge

| Caso | Acción |
|---|---|
| Empleado nuevo sin NSS | Patrón está obligado a registrarlo en IMSS — bloquear nómina hasta resolver |
| Empleado con incapacidad IMSS (subsidio) | NO pagar días IMSS + ajustar CFDI con "incapacidad" |
| Empleado con ISR retenido > subsidio empleo | Retener ISR pos-subsidio (negativo = sub paga, positivo = empleado paga) |
| Cambio de SBC mid-mes | Recalcular IMSS proporcional |
| Bono o vale despensa | Sumar a CFDI con clave correcta (impacto fiscal distinto) |
| Empleado con embargo judicial | Aplicar descuento conforme orden judicial (hasta 30% LFT Art. 110) |
| Patrón con varios registros patronales | Cada empleado vinculado al registro correcto |
| Empleado fallece | Liquidación + finiquito + indemnización + reporte IMSS especial |

## 9. Dependencias

- **MCPs**: `mp_facturama_extendido` (CFDI Nómina), `mp_imss_patronal` (consultas IDSE), `mp_infonavit_patronal` (consulta créditos), `mp_sat_portal` (RFC empleados, padrón)
- **MCPs nuevos sugeridos**:
  - `mp_sua_export` — generador archivo .SUA del IMSS (no API, formato fijo)
  - `mp_dispersion_bancos` — multi-banco SPEI batch (extensión `mp_bancos_mx`)
- **Skills `_shared/`**: cfdi-emision, iva-retenciones-mx, rfc-validacion, mxn-formato, whatsapp-business-mx, compliance-lfpdppp

## 10. Criterios de aceptación

- [ ] Plugin con plugin.json + 10 skills + 6 commands + workflow
- [ ] CFDI Nómina 4.0 + Complemento 1.2 Rev. E correcto
- [ ] Cálculo ISR Art. 96 con tarifa salarios + subsidio empleo aplicable
- [ ] SBC con factor de integración correcto (1.0452 mínimo + variables fijos/variables)
- [ ] IDSE: archivo .SUA generado validable
- [ ] Recibo PDF profesional al empleado
- [ ] Cierre quincenal genera < 60 segundos para 50 empleados
- [ ] Tests con 8 fixtures
- [ ] Compliance LFPDPPP en datos empleados

## 11. Esfuerzo estimado

- **Scaffold**: 5-10h
- **10 skills**: 100-160h
- **Workflow corrida + dispersión**: 40-60h
- **Cálculos ISR salarios + subsidio empleo**: 30-50h (tarifa anual)
- **Cuotas IMSS (5 ramos: enfer, mater, invalidez, riesgo, retiro)**: 40-60h
- **Generación archivo .SUA (formato propietario)**: 50-80h
- **Generación PDF recibo profesional**: 20-30h
- **Tests + 8 fixtures**: 40-60h
- **Docs**: 25-40h
- **Validación con contador especializado nómina**: 5-10h coordinación
- **TOTAL**: **355-560 horas** (~9-14 semanas FT)

## 12. Riesgos + mitigaciones

| Riesgo | Prob | Impacto | Mitigación |
|---|---|---|---|
| Tarifa ISR salarios cambia (RMF cada enero) | **Alta** | Crítico | Catálogo separado + validación enero |
| Cuotas IMSS cambian (SBC mínimo, factor) | **Alta (anual)** | Crítico | Catálogo separado |
| Subsidio empleo cambia tope | Media | Alto | Catálogo separado |
| Errar CFDI Nómina = multa | Media | Crítico | Validador pre-timbrado + hook lo está cubriendo |
| Error en SUA = capital constitutivo IMSS | Baja | **CRÍTICO** (puede quebrar) | Doble check vs sistema IMSS oficial antes de presentar |
| Empleado reclama por sueldo mal calculado | Media | Alto | Tracking detallado + recibos firmados |

## 13. Decisiones pendientes

- [ ] ¿Generar archivo SUA con formato 2026 (validar contra IMSS)?
- [ ] ¿Dispersión bancaria multi-banco (BBVA, Banamex, Santander, Banorte)?
- [ ] ¿Pricing: $999 MXN/mes hasta 10 empleados, +$50/empleado adicional?
- [ ] ¿Soporte para asimilados a salarios (caso edge común con freelancers)?

## 14. Plan de implementación

### Fase 1: Scaffold (5-10h)
1. plugin.json + README
2. Estructura folders

### Fase 2: Catálogos + cálculos (50-80h)
1. Tarifa ISR Art. 96 + tabla subsidio empleo
2. Tabla cuotas IMSS (5 ramos)
3. Factor integración (LFT Art. 84)
4. Catálogo conceptos CFDI Nómina (claves SAT)

### Fase 3: Skills empleado base (50-80h)
- alta-empleado-completa, baja-empleado-imss
- calculo-isr-salarios-art96, cuotas-imss-sbc, cuotas-infonavit-5pct

### Fase 4: CFDI Nómina (50-80h)
- cfdi-nomina-quincenal con timbrado real
- Validador previo

### Fase 5: SUA + IDSE (50-80h)
- sua-idse-export (formato fijo IMSS)
- Validación contra sistema oficial

### Fase 6: Anuales (30-50h)
- aguinaldo-y-ptu-anual
- vacaciones-prima-vacacional

### Fase 7: Dashboard + workflow (40-60h)
- dashboard-nomina-quincenal
- workflow-corrida-nomina-quincenal

### Fase 8: Tests + docs (40-80h)

## 15. Links

- [SAT - Preguntas Complemento Nómina](http://omawww.sat.gob.mx/tramitesyservicios/Paginas/Preguntas_frecuentes_Nomina_1_2.htm)
- [XPD - Guía CFDI Nómina 2026](https://xpd.mx/blog/como-emitir-un-cfdi-de-nomina-4-0-y-su-complemento-1-2.html)
- [SAT - Guía Nómina 2026 ContadorMX](https://contadormx.com/guia-de-la-nomina-del-sat-2026/)
- [Revisión E del Complemento 1.2 - DOF 29 dic 2025](http://dof.gob.mx)
- [Art. 99 LISR - Obligaciones del patrón](https://www.diputados.gob.mx/LeyesBiblio/pdf/LISR.pdf)
- [LFT Art. 84-87 - Salario integrado, aguinaldo, vacaciones](https://www.diputados.gob.mx/LeyesBiblio/pdf/125_122025.pdf)
