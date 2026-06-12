---
spec: "vertical-crowdfunding-itf-mx"
estado: "DRAFT"
creado: "2026-06-12"
autor: "Elías Rashid Morales Mendoza"
ultima_actualizacion: "2026-06-12"
esfuerzo_estimado_horas: [350, 580]
prioridad: "tier-3"
---

# Spec 14 — Vertical `crowdfunding-itf-mx`

## 1. Propósito

Plugin para **PYMES y emprendedores que operan o invierten en plataformas de Financiamiento Colectivo (IFC)** reguladas por la Ley Fintech 2018 en México. Cubre 3 perfiles:

1. **Emprendedor que solicita financiamiento** (debt o equity crowdfunding)
2. **Inversionista P2P** que presta a través de plataformas como Kueski, Doopla, etc.
3. **Operador de IFC autorizada por CNBV** (cumplimiento regulatorio)

Mercado: ~70 IFC autorizadas por CNBV (2025), con miles de inversionistas P2P.

## 2. Contexto y por qué es novedoso

- **Ley Fintech 2018 + DCG Fintech CNBV** vigente: México fue el primer país de LatAm con regulación formal
- **3 tipos de crowdfunding** según Ley Fintech:
  - Deuda (P2P loans): inversor presta, recibe principal + intereses
  - Capital (equity): inversor compra acciones de PyME
  - Copropiedad/regalías: inversor recibe % de ingresos futuros del proyecto
- **Tope inversión PF** por proyecto regulado: ~$100k MXN base (mayor si "inversionista experimentado")
- **Tope financiamiento** por proyecto: hasta ~$22M MXN
- **Compliance ITF**: KYC + AML + reportes mensuales CNBV
- **Fiscal**: rendimientos = intereses → tarifa retención específica + IVA del servicio plataforma 16%

## 3. Alcance

**Dentro:**
- Para emprendedor: comparador de IFC por tipo (deuda/equity) + tasas + plazos
- Para emprendedor: simulador costo total financiamiento via crowdfunding vs banco
- Para inversionista: dashboard portfolio P2P (capital prestado + rendimientos pendientes + en mora)
- Para inversionista: cálculo fiscal de rendimientos (ISR sobre intereses + retención plataforma)
- Para inversionista: diversificación (concentración por proyecto, por industria)
- Para operador IFC: checklist compliance CNBV (reportes mensuales, capital mínimo)
- Para operador IFC: gestión de KYC/AML básico (umbral $10k USD)
- Catálogo de las IFC autorizadas vigentes (CNBV publica lista)

**Fuera (decisión deliberada):**
- Plataformas internacionales (Kickstarter, Indiegogo) — no son IFC mexicanas
- Crowdfunding equity privado (sin IFC) — ofertas privadas reguladas por CNBV otra forma
- Activos virtuales (cripto) en IFC — Ley Fintech permite pero requerimientos extra
- Sandbox regulatorio CNBV (programa especial — fuera de scope normal)

## 4. Inputs / outputs / schemas

### Inversionista P2P

```python
class InversionistaP2P(BaseModel):
    rfc: str
    plataformas_activas: list[str]  # ["doopla", "kueski_capital", "yotepresto"]
    capital_total_invertido_mxn: Decimal
    capital_disponible_mxn: Decimal
    estado_inversionista: Literal["normal", "experimentado"]  # afecta tope por proyecto
    proyectos_activos: list[ProyectoInversion]
```

### Proyecto inversión P2P

```python
class ProyectoInversion(BaseModel):
    proyecto_id: str
    plataforma: str
    tipo: Literal["deuda", "capital", "regalias"]
    industria: str
    monto_invertido_mxn: Decimal
    tasa_anual_pactada: float
    plazo_meses: int
    fecha_inicio: date
    fecha_termino: date
    pagos_recibidos: list[Pago]
    pagos_pendientes: list[Pago]
    estado: Literal["al_corriente", "atrasado_30d", "atrasado_60d", "moroso", "incobrable", "completado"]
    riesgo_calificado: Literal["A", "B", "C", "D"]  # rating de la plataforma
```

## 5. Skills propuestos (10)

| Skill | Cuándo activa |
|---|---|
| `dashboard-portfolio-p2p` | Inversionista status |
| `simulador-costo-financiamiento-cf` | Emprendedor evalúa CF vs banco |
| `comparador-ifc-autorizadas` | Listado vigente + tasas |
| `fiscal-rendimientos-p2p` | ISR sobre intereses + retención |
| `diversificacion-portfolio` | Concentración por proyecto |
| `tracking-pagos-recibidos-p2p` | Por proyecto |
| `compliance-tope-100k-pf` | Validar inversor PF |
| `kyc-aml-basico-ifc` | Si operador IFC |
| `reporte-mensual-cnbv` | Para IFC autorizadas |
| `catalogo-ifc-vigentes` | Lista CNBV |

## 6. Comandos (5)

```
/cf:dashboard
/cf:comparar
/cf:fiscal
/cf:catalogo-ifc
/cf:compliance
```

## 7. Workflow

`workflow-cierre-mensual-p2p.md`:
1. Cargar plataformas conectadas
2. Por cada una: descargar movimientos del mes (pagos recibidos, intereses, default)
3. Reconciliar con tracker interno
4. Calcular rendimientos del mes (capital recuperado + intereses)
5. Calcular ISR causado por intereses
6. Generar reporte fiscal mensual
7. Identificar proyectos en mora → estrategia

## 8. Casos edge

| Caso | Acción |
|---|---|
| Inversor PF cerca del tope $100k por proyecto | Validar antes de invertir |
| Inversor "experimentado" (declaración voluntaria) | Tope mayor — registrar criterio |
| Proyecto en default total | Pérdida deducible si plataforma certifica incobrable |
| Plataforma IFC pierde autorización CNBV | Recuperación complicada — protocolo |
| Rendimientos en cripto (algunas IFC) | Conversión a MXN + tratamiento cripto |
| Inversor con varias plataformas | Consolidar agregadamente |
| Capital + intereses no devueltos | Tracking morosidad escalado |
| Operador IFC sin reporte mensual CNBV | Multas + posible cancelación |

## 9. Dependencias

- **MCPs**: `mp_sat_portal` (RFC validar inversores/emprendedores)
- **MCPs nuevos sugeridos**:
  - `mp_cnbv_ifc_catalogo` — lista oficial IFC autorizadas (scrape CNBV)
  - `mp_doopla_api`, `mp_kueski_capital_api`, `mp_yotepresto_api` — específicas (algunas tienen API pública)
- **Skills `_shared/`**: cfdi-emision, mxn-formato, rfc-validacion, compliance-lfpdppp

## 10. Criterios de aceptación

- [ ] Plugin completo
- [ ] Catálogo de las top 20 IFC autorizadas vigentes
- [ ] Simulador costo financiamiento CF vs banco para emprendedor
- [ ] Dashboard portfolio P2P con concentración + morosidad
- [ ] Cálculo fiscal rendimientos correcto
- [ ] Tope $100k validador para PF normal
- [ ] Tests con 5 fixtures (inversor normal, experimentado, emprendedor, operador IFC, default)
- [ ] Lint passing

## 11. Esfuerzo estimado

- **Scaffold**: 5-10h
- **Catálogo IFC autorizadas + scraping**: 30-50h
- **10 skills**: 100-160h
- **Simulador costo CF**: 30-50h
- **Dashboard portfolio P2P**: 40-60h
- **Cálculo fiscal rendimientos**: 30-50h
- **Compliance KYC/AML básico**: 50-80h
- **Reporte mensual CNBV (si operador)**: 50-80h
- **Tests + 5 fixtures**: 30-50h
- **Docs + compliance**: 25-40h
- **Validación con regulador / abogado fintech**: 10-20h coordinación
- **TOTAL**: **400-650 horas** (~10-16 semanas FT)

## 12. Riesgos + mitigaciones

| Riesgo | Prob | Impacto | Mitigación |
|---|---|---|---|
| Ley Fintech reforma sustancial | Media | Crítico | Diseño modular + revisión anual |
| IFC autorizada quiebra | Media | Alto | Diversificación obligatoria en dashboard |
| Tope $100k cambia | Baja | Alto | Catálogo separado |
| Plataforma no expone API | Alta | Medio | CSV manual + reconciliación |
| Compliance KYC/AML errado = multa CNBV | Baja | Crítico | Pedir asesoría regulatoria para operadores IFC |

## 13. Decisiones pendientes

- [ ] ¿Producto para inversionista (B2C $399 MXN/mes) o para operador IFC ($24k MXN/mes)?
- [ ] ¿Integración API directa con top 5 IFC o solo CSV?
- [ ] ¿Soportar sandbox regulatorio CNBV (programa innovador)?

## 14. Plan de implementación

### Fase 1: Scaffold + catálogo IFC (35-60h)
### Fase 2: Skills inversionista P2P (80-130h)
### Fase 3: Skills emprendedor CF (40-60h)
### Fase 4: Compliance + KYC/AML (110-160h)
### Fase 5: Tests + docs (75-130h)

## 15. Links

- [CNBV - Disposiciones Fintech ITF](https://www.cnbv.gob.mx/Normatividad/Disposiciones%20de%20car%C3%A1cter%20general%20aplicables%20a%20las%20instituciones%20de%20tecnolog%C3%ADa%20financiera.pdf)
- [Legal Paradox - Ley Fintech México 2026](https://www.legalparadox.com/es/ley-fintech)
- [Ley LRITF - texto completo](https://www.diputados.gob.mx/LeyesBiblio/pdf/LRITF.pdf)
- [Comunicado CNBV - Créditos via IFC](https://www.gob.mx/cnbv/prensa/comunicado-no-68-cnbv-informa-sobre-la-obtencion-de-creditos-a-traves-de-instituciones-de-financiamiento-colectivo)
- [Senado - Estudio ITF + Ley Fintech](http://bibliodigitalibd.senado.gob.mx/bitstream/handle/123456789/5519/ML_214.pdf?sequence=1&isAllowed=y)
- [CONDUSEF - Sobre fintech e ITF](https://www.condusef.gob.mx/index.php/material-educativo?p=contenido&idc=1671&idcat=1)
