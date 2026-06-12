---
spec: "vertical-pf-anual-mx"
estado: "DRAFT"
creado: "2026-06-11"
autor: "Elías Rashid Morales Mendoza"
ultima_actualizacion: "2026-06-11"
esfuerzo_estimado_horas: [300, 500]
prioridad: "tier-1"
---

# Spec 05 — Vertical `pf-anual-mx` (declaración anual ISR)

## 1. Propósito

Vertical de **mayor score del research (9.5/10)** — declaración anual ISR para persona física en México. Mercado: ~5M declarantes anuales obligados.

Cubre:
- Captura de CFDIs emitidos+recibidos del año completo (vía `mp_sat_portal`)
- Identificación automática de deducciones personales aplicables (Art. 151)
- Cálculo ISR según régimen (PFAE, RESICO PF, asalariado con honorarios)
- Comparativa contra pagos provisionales acumulados
- Generación de borrador presentable + línea de captura
- Saldo a favor vs saldo a pagar

Genera revenue desde **abril** (deadline 30 abril cada año).

## 2. Contexto y por qué es novedoso

- **Lo que existe**: `workflow-pf-anual-completa` en `core-mexico/agents/`. Es un workflow que coordina MCPs.
- **Por qué es novedoso**: este sería un **plugin completo dedicado** con UX optimizada para el ciclo anual:
  - Pre-temporada (enero-febrero): preparación
  - Temporada (marzo-abril): declaración
  - Post-temporada (mayo-junio): seguimiento devoluciones / pagos
- **No es solo el workflow**: incluye skills específicos, comandos slash optimizados, dashboard del año, comparativa con años previos, tracking de devolución solicitada.
- **Combina múltiples MCPs** de formas nuevas: `mp_sat_portal` (CFDIs masivos) + `mp_banxico` (UMA/INPC) + `mp_facturama_extendido` (validación) + `mp_aspel_contpaqi` (si usa contador) + bancos para cruce.

## 3. Alcance

**Dentro:**
- Plugin `pf-anual-mx/` con plugin.json y dependencia obligatoria de `core-mexico`
- 6-8 skills propios específicos del proceso anual
- 5 comandos slash optimizados
- 1-2 agents/workflows orquestadores
- Dashboard inicial con status del año fiscal
- Soporte para 3 regímenes: PFAE (612), RESICO PF (626), Asalariado + honorarios (605+612)

**Fuera (decisión deliberada):**
- PM (persona moral) — vertical aparte
- Régimen pensiones/jubilación — caso edge
- Honorarios asimilados a salarios — caso edge
- Pagos provisionales **mensuales** (eso es `cierre-fiscal-mensual` del core)
- Asesoría legal-fiscal personalizada (la app sugiere, contador valida)

## 4. Inputs / outputs / schemas

### Inputs del usuario

```python
class DeclaracionAnualInput(BaseModel):
    rfc: str
    ejercicio: int  # ej. 2025
    regimen: Literal["PFAE_612", "RESICO_PF_626", "ASALARIADO_HONORARIOS_605"]
    fuentes_ingreso: list[Literal[
        "honorarios", "arrendamiento", "actividad_empresarial",
        "sueldos", "enajenacion_bienes", "intereses"
    ]]
    incluir_deducciones_personales: bool = True
    incluir_validacion_buzon: bool = True
```

### Output

```python
class DeclaracionAnualResultado(BaseModel):
    rfc_hash: str
    ejercicio: int
    regimen: str

    # Ingresos consolidados
    ingresos_acumulables_mxn: Decimal
    ingresos_exentos_mxn: Decimal

    # Deducciones
    deducciones_acumulables_mxn: Decimal
    deducciones_personales_capturadas_mxn: Decimal
    deducciones_personales_aplicables_mxn: Decimal  # con tope
    tope_aplicado: Literal["5_UMAs_anuales", "15_pct_ingresos", "ninguno"]

    # Cálculo
    utilidad_fiscal_mxn: Decimal
    isr_anual_calculado_mxn: Decimal
    pagos_provisionales_acumulados_mxn: Decimal
    isr_retenido_acumulado_mxn: Decimal
    diferencia_mxn: Decimal  # negativa = saldo favor

    # Acción
    resultado: Literal["SALDO_A_PAGAR", "SALDO_A_FAVOR", "EXACTO"]
    fecha_limite_presentacion: date
    linea_captura: str | None
    siguientes_pasos: list[str]
    alertas: list[str]
    vigencia_validada: bool  # False hasta contador revise
```

## 5. Skills propuestos (8)

| Skill | Cuándo activa |
|---|---|
| `dashboard-anual-fiscal` | "como va mi declaración anual", "status año fiscal" |
| `recopilar-cfdis-anuales` | Descarga masiva 12 meses |
| `cruzar-bancos-vs-cfdis` | Detectar depósitos sin facturar |
| `identificar-deducciones-personales` | Salud, hipoteca, donativos, intereses, etc. |
| `calculadora-isr-anual` | Aplicar tarifa Art. 96 LISR o RESICO ladder |
| `generar-borrador-declaracion` | Output presentable (PDF + JSON) |
| `seguimiento-devolucion-sat` | Tracking semanal de devolución solicitada |
| `alertas-deadline-anual` | Calendario fiscal + recordatorios |

Skills heredados de `core-mexico`: cfdi-emision, iva-retenciones-mx, rfc-validacion, whatsapp-business-mx, compliance-lfpdppp, mxn-formato.

## 6. Comandos propuestos (5)

```
/pf-anual:dashboard               # Status del año fiscal en curso
/pf-anual:recopilar               # Descarga masiva todos los CFDIs
/pf-anual:calcular                # Cálculo + comparativa con provisionales
/pf-anual:borrador                # Genera PDF presentable
/pf-anual:status-devolucion       # Seguimiento si solicitaste devolución
```

## 7. Workflow orquestador

Reutilizar `workflow-pf-anual-completa` (ya existe en core-mexico) + extender con:
- Phase 0: validación de régimen (capturar si no está claro)
- Phase 1-4: idénticas al actual
- Phase 5 (nueva): scoring de riesgo (saldo > $50k a favor = SAT revisa)
- Phase 6 (nueva): borrador PDF generado
- Phase 7 (nueva): registrar en tracker anual

## 8. Casos edge

| Caso | Comportamiento |
|---|---|
| Cliente cambió régimen mid-año (PFAE → RESICO) | Calcular ambos periodos por separado |
| Ingresos > $3.5M en RESICO PF | Notificar que ya no aplica RESICO, recalcular como PFAE |
| Persona con sueldos + honorarios + arrendamiento | Acumular todos como ingresos |
| Sin CFDIs recibidos (no dedujo nada) | Permitir continuar — usar deducciones personales solo |
| CFDIs con RFC en lista 69-B definitivo | **Excluir** del cálculo de deducciones |
| Saldo a favor > $100k | Alerta crítica — SAT puede pedir auditoría |
| Cliente quiere usar deducción ciega vs comprobada | Comparar ambos escenarios |
| Año anterior con saldo a favor no devuelto | Sumar como acreditamiento |
| Cliente fallecido (sucesión) | Caso especial — derivar a contador |

## 9. Dependencias

- **MCPs**: `mp_sat_portal` (CFDIs masivos), `mp_banxico` (UMA/INPC), `mp_facturama_extendido` (validar CFDIs), `mp_aspel_contpaqi` (si usa contador), `mp_bancos_mx` (cruces)
- **Workflows**: `workflow-pf-anual-completa` (extendido)
- **Skills `_shared/`**: cfdi-emision, iva-retenciones-mx, rfc-validacion, mxn-formato

## 10. Criterios de aceptación

- [ ] Plugin completo con plugin.json + 8 skills propios + 5 commands
- [ ] `dashboard-anual-fiscal` lista estado del año al iniciar sesión
- [ ] `recopilar-cfdis-anuales` descarga 12 meses (vía `sat_descargar_cfdi_masivo`)
- [ ] `calculadora-isr-anual` calcula con tarifa Art. 96 LISR + ajustes UMA
- [ ] Deducciones personales toperadas a 5 UMAs anuales o 15% (lo menor)
- [ ] Borrador genera PDF profesional con desglose por capítulo
- [ ] Marca `vigencia_validada: false` hasta contador firme
- [ ] Tests con 3 fixtures: PFAE saldo pagar, RESICO PF saldo favor, asalariado mixto
- [ ] Lint passing
- [ ] Score honesto > 6/9 (con tarifas vigencia validar)

## 11. Esfuerzo estimado

- **Scaffold plugin + plugin.json**: 5-10h
- **8 skills SKILL.md + references**: 80-120h (~10-15h/skill)
- **5 comandos**: 15-25h
- **Workflow extendido**: 20-40h
- **Dashboard + reporting**: 30-50h
- **Generación PDF**: 25-40h
- **Tests + fixtures (8+)**: 30-50h
- **Docs + guía vertical**: 20-30h
- **Validación inicial con contador (no codificable)**: 10-20h coordinación
- **TOTAL**: **235-385 horas** (~6-10 semanas FT)

⚠ Para llegar a score 7.5/9 (producción-grade) requiere validación con contador certificado adicionalmente (~$3-8k MXN consultoría externa).

## 12. Riesgos + mitigaciones

| Riesgo | Prob | Impacto | Mitigación |
|---|---|---|---|
| Tarifa Art. 96 LISR cambia anualmente | **Alta (cada enero)** | Crítico | Catálogo separado + validación cada enero |
| Tope deducciones personales cambia | Media | Alto | Mismo enfoque catálogo |
| Cálculo incorrecto = multa cliente | Baja | **CRÍTICO** | Marca `vigencia_validada: false` hasta contador OK |
| SAT cambia formato declaración | Baja-Media | Alto | Borrador no presenta — guía al usuario |
| Saldo a favor solicitado y rechazado | Media | Bajo | Sistema documenta razones probables |
| Usuario sin todos los CFDIs | Alta | Medio | Asistente identifica gaps + sugiere acciones |

## 13. Decisiones pendientes

- [ ] ¿Generar el borrador en formato compatible con DeclaraSAT directamente, o solo PDF?
- [ ] ¿Incluir asistente conversacional para captura de deducciones personales (chat-style)?
- [ ] ¿Comparativa con años previos (requiere histórico)?
- [ ] ¿Pricing como producto: $499 MXN flat fee por año / cliente?
- [ ] ¿Marca "validado por contador" como upgrade premium?

## 14. Plan de implementación

### Fase 1: Scaffold (5-10h)
1. `pf-anual-mx/.claude-plugin/plugin.json`
2. README + CHANGELOG
3. Estructura de carpetas
4. `sync-shared.sh pf-anual-mx`

### Fase 2: Skills propios (80-120h, paralelizable)
1. `dashboard-anual-fiscal/SKILL.md`
2. `recopilar-cfdis-anuales/SKILL.md`
3. `cruzar-bancos-vs-cfdis/SKILL.md`
4. `identificar-deducciones-personales/SKILL.md`
5. `calculadora-isr-anual/SKILL.md` (CRÍTICO — con tarifa Art. 96)
6. `generar-borrador-declaracion/SKILL.md`
7. `seguimiento-devolucion-sat/SKILL.md`
8. `alertas-deadline-anual/SKILL.md`

### Fase 3: Workflow + commands (35-65h)
1. Extender `workflow-pf-anual-completa` con Phases 5-7
2. 5 commands

### Fase 4: Generación PDF (25-40h)
1. Plantilla profesional (reportlab o weasyprint)
2. Tabla por capítulo
3. Footer con disclaimer "no validado por contador"

### Fase 5: Tests + fixtures (30-50h)
1. 3 fixtures por régimen
2. Tests unitarios calculadora
3. Tests de integración con mock MCPs

### Fase 6: Docs (20-30h)
1. `docs/guia-vertical-pf-anual.md`
2. Casos de uso documentados
3. Update STATUS.md

## 15. Links

- Research original: score 9.5/10
- `workflow-pf-anual-completa` actual: `core-mexico/agents/`
- Art. 96 LISR (tarifa): consultar RMF vigente
- DeclaraSAT portal: https://www.sat.gob.mx/declaracion/19608/declaracion-anual-personas-fisicas
