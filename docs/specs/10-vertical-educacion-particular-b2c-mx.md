---
spec: "vertical-educacion-particular-b2c-mx"
estado: "DRAFT"
creado: "2026-06-12"
autor: "Elias"
ultima_actualizacion: "2026-06-12"
esfuerzo_estimado_horas: [220, 380]
prioridad: "tier-2"
---

# Spec 10 — Vertical `educacion-particular-b2c-mx`

## 1. Propósito

Plugin para **profesionales y pymes** que ofrecen cursos / educación online B2C en México:
- Tutores privados (matemáticas, idiomas, música)
- Academias online (cursos digitales)
- Coaches con cursos de pago
- Bootcamps especializados (tecnología, marketing)
- Plataformas de educación continua

Mercado: ~80k creadores de cursos en México (Hotmart + Eduzz + Teachable + propios).

Diferencia clave vs `colegios-mx`: `colegios-mx` cubre **escuelas oficiales con RVOE** (preescolar a bachillerato); este vertical cubre **educación particular B2C sin RVOE típicamente**.

## 2. Contexto y por qué es novedoso

- **CFDI uso D10** (Pagos por servicios educativos): aplica **SOLO si la escuela tiene RVOE** y el alumno está en preescolar/primaria/secundaria/bachillerato. Cursos online de coding bootcamp → NO uso D10.
- **Tope deducible** por nivel (Art. 151 LISR):
  - Preescolar: $14,200/año
  - Primaria: $12,900/año
  - Secundaria: $19,900/año
  - Bachillerato: $24,500/año
- **Cursos online B2C** (bootcamps, idiomas, música) → CFDI uso G03 (gastos en general), **NO deducibles** como colegiatura para el alumno
- **Complemento IEDU** (Instituciones Educativas) obligatorio en CFDIs con uso D10
- **No hay vertical actual** para creadores B2C — solo escolar formal

## 3. Alcance

**Dentro:**
- Inscripción de alumnos / clientes (CRM ligero)
- CFDI mensual / por curso uso G03 (educación particular sin RVOE)
- Si la academia es una **escuela con RVOE** (raro): CFDI uso D10 + Complemento IEDU
- Pagos recurrentes mensuales (suscripción curso) con cobranza escalada
- Tracking de progreso del alumno (módulos completados)
- Certificados de finalización (PDF firmados)
- Refund policies + emisión nota crédito
- Marketing post-venta (recordatorio cobranza, up-sell siguiente curso)

**Fuera (decisión deliberada):**
- Escuelas con RVOE (eso es `colegios-mx`)
- Plataformas marketplace (Hotmart, Udemy) — el creador opera en ellas pero los CFDIs los emite la plataforma
- LMS completo (no construimos LMS, integramos via webhook)
- Educación universitaria (otra escala + regulación SEP)

## 4. Inputs / outputs / schemas

### Curso

```python
class Curso(BaseModel):
    id: str
    titulo: str
    categoria: str
    precio_mxn: Decimal
    es_recurrente: bool        # cobro mensual vs one-shot
    duracion_meses: int | None
    tiene_certificado: bool
    tiene_RVOE: bool           # raro en B2C — si sí, uso D10
    nivel_educativo_RVOE: Literal["preescolar","primaria","secundaria","bachillerato"] | None
```

### Alumno

```python
class Alumno(BaseModel):
    rfc: str | None            # opcional — XAXX si público en general
    nombre: str
    curp: str | None
    email: str
    tel_wa: str
    fecha_inscripcion: date
    cursos_activos: list[str]
    progreso: dict[str, float]  # curso_id → % completado
    estado_pago: Literal["al_corriente", "atrasado", "moroso"]
```

## 5. Skills propuestos (8)

| Skill | Cuándo activa |
|---|---|
| `dashboard-cursos-mes` | Ingresos + alumnos activos |
| `inscripcion-alumno` | Onboarding |
| `cfdi-mensualidad-curso` | CFDI uso G03 (o D10 si RVOE) |
| `cobranza-mensualidades` | Cobranza recurrente |
| `tracking-progreso-curso` | Status alumno |
| `emisión-certificado` | PDF firmado al completar |
| `up-sell-siguiente-curso` | Marketing post-venta |
| `complemento-iedu-cfdi-d10` | Si academia con RVOE |

## 6. Comandos (5)

```
/edu:dashboard
/edu:inscribir
/edu:facturar
/edu:cobranza
/edu:certificados
```

## 7. Workflow

`workflow-mes-academia-online.md`:
1. Identificar alumnos con cobro recurrente del mes
2. Emitir CFDI uso G03 (o D10 si aplica)
3. Cobranza nivel 1 (D-3 recordatorio)
4. Verificar pagos en cuenta
5. Generar certificados a quienes completaron el mes
6. Identificar candidatos a up-sell

## 8. Casos edge

| Caso | Acción |
|---|---|
| Alumno pide CFDI deducible | Validar — solo deducible si tiene RVOE + alumno en nivel educativo |
| Alumno extranjero sin RFC | XAXX010101000 — no deducible para alumno |
| Refund mid-curso | Nota crédito + ajuste pago próximo |
| Alumno paga 1 año adelantado | CFDI por anualidad — facturación adelantada |
| Curso gratis (lead magnet) | Sin CFDI — solo registro alumno |
| Curso patrocinado por empresa (B2B híbrido) | CFDI a empresa, no a alumno |
| Bootcamp con financiamiento ISA | Estructura más compleja — V2 |
| Alumno reporta fraude (no recibió producto) | Refund + protocolo soporte |

## 9. Dependencias

- **MCPs**: `mp_facturama_extendido` (CFDI G03 o D10), `mp_sat_portal` (validación RFC alumno), `mp_meta_whatsapp` (cobranza), `mp_conekta` o `mp_mercado_pago` o `mp_stripe` (procesador de pago recurrente)
- **Skills `_shared/`**: cfdi-emision, mxn-formato, whatsapp-business-mx, compliance-lfpdppp

## 10. Criterios de aceptación

- [ ] Plugin completo
- [ ] CFDI G03 normal + CFDI D10 con Complemento IEDU si academia RVOE
- [ ] Tracking de progreso por alumno
- [ ] Certificados PDF profesionales con firma
- [ ] Cobranza recurrente escalada
- [ ] Tests con 5 fixtures
- [ ] Lint passing

## 11. Esfuerzo estimado

- **Scaffold**: 5-10h
- **8 skills**: 80-130h
- **Workflow + cobranza recurrente**: 30-50h
- **Generación certificados PDF**: 20-30h
- **Complemento IEDU CFDI D10**: 25-40h
- **Integración procesador pago recurrente**: 30-50h
- **Tests + 5 fixtures**: 25-40h
- **Docs**: 15-30h
- **TOTAL**: **230-380 horas** (~6-10 semanas FT)

## 12. Riesgos + mitigaciones

| Riesgo | Prob | Impacto | Mitigación |
|---|---|---|---|
| Alumno reclama por no poder deducir | Media | Bajo | Disclaimer claro al inscribir: "Educación particular sin RVOE NO es deducible" |
| Topes CFDI D10 cambian | Baja | Bajo | Catálogo separado |
| Procesador pago bloquea por chargeback alto | Media | Alto | Refund policy clara + soporte rápido |
| Plataforma LMS externa cambia API | Media | Bajo | Adaptador modular |

## 13. Decisiones pendientes

- [ ] ¿LMS propio o integrar con LMS externo (Thinkific, Teachable)?
- [ ] ¿Procesador pago default: Conekta, Stripe, o Mercado Pago?
- [ ] ¿Pricing: $499 MXN/mes o % por venta?

## 14. Plan de implementación

### Fase 1: Scaffold (5-10h)
### Fase 2: Inscripción + CRM (30-50h)
### Fase 3: CFDI G03 + Complemento IEDU (50-80h)
### Fase 4: Cobranza recurrente (40-60h)
### Fase 5: Certificados (20-30h)
### Fase 6: Tests + docs (50-80h)

## 15. Links

- [SAT - Colegiaturas deducibles](https://www.sat.gob.mx/minisitio/DeduccionesPersonales/colegiaturas.html)
- [Heru - Colegiaturas deducibles 2026 niveles límites](https://www.heru.app/blog/colegiaturas-deducibles-en-el-sat-niveles-limites-y-requisitos-2026/)
- [XPD - Complemento IEDU](https://xpd.mx/blog/complemento-iedu-como-facturar-colegiaturas-correctamente.html)
- [Expansion - CFDI colegiatura 2026](https://expansion.mx/finanzas-personales/2026/03/12/como-factura-colegiatura-deducible-declaracion-anual-sat)
