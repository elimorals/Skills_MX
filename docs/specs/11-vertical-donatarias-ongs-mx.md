---
spec: "vertical-donatarias-ongs-mx"
estado: "DRAFT"
creado: "2026-06-12"
autor: "Elias"
ultima_actualizacion: "2026-06-12"
esfuerzo_estimado_horas: [300, 500]
prioridad: "tier-2"
---

# Spec 11 — Vertical `donatarias-ongs-mx`

## 1. Propósito

Plugin para **organizaciones civiles autorizadas como donatarias** (Art. 79 LISR) en México. Mercado: ~9,500 donatarias autorizadas (lista SAT vigente 2025).

Resuelve los **dolores recurrentes** de la donataria pequeña/mediana:
1. Declaración informativa anual de transparencia (31 mayo, multas alta si se omite)
2. CFDI a donantes con uso D04 (donativos deducibles)
3. Reportes mensuales: retenciones, donativos en efectivo > $100k, operaciones partes relacionadas
4. Renovación anual de autorización (la pierden ~10% donatarias por incumplimiento)
5. Compliance LFPRH (Ley Federal Prevención Riesgo Financiero) para donativos > $100k

## 2. Contexto y por qué es novedoso

- **No hay vertical de ONG**: ningún plugin actual cubre el régimen 401 (donatarias autorizadas)
- **Reformas 2026 SAT**: nuevas reglas más estrictas — INFOBAE marzo 2026 reporta endurecimiento (validación objeto social, listas de actividades)
- **Declaración anual transparencia**: obligatoria todos los años, vence 31 mayo del año siguiente al ejercicio, sanción 2-100% del patrimonio si se omite
- **CFDI D04**: emitido por donataria al donante; donante puede deducir hasta 7% del ingreso del año anterior
- **Padrón actualizado SAT**: lista publicada en Anexo 14 de RMF (puede dejar de aparecer si no cumple obligaciones)

## 3. Alcance

**Dentro:**
- Onboarding donantes (PF/PM) con captura datos
- CFDI tipo I uso D04 al donante (con datos de donataria oficial)
- Tracking donativos recibidos por mes (efectivo, transferencia, especie)
- Reporte mensual donativos efectivo > $100k (LFPRH)
- Declaración informativa anual de transparencia (formato SAT)
- Tracking de actividades realizadas (objeto social)
- Renovación anual de autorización (alertas + documentos requeridos)
- Reporte ingresos / egresos / remanente distribuible

**Fuera (decisión deliberada):**
- Donatarias internacionales (otra regulación)
- Fideicomisos (estructura específica + abogado)
- Asociaciones religiosas (régimen distinto 502)
- ONGs sin autorización SAT (no pueden emitir CFDI D04)
- Auditoría externa anual (servicio profesional aparte)

## 4. Inputs / outputs / schemas

### Donataria

```python
class Donataria(BaseModel):
    rfc: str
    razon_social: str
    folio_autorizacion_sat: str  # número en Anexo 14 RMF
    fecha_autorizacion_inicial: date
    fecha_renovacion_proxima: date
    objeto_social_principal: str  # asistencial, cultural, científica, etc.
    actividades_autorizadas: list[str]
    auditor_externo_dictamen: bool  # algunos casos obligatorio
    e_firma_disponible: bool
```

### Donativo

```python
class Donativo(BaseModel):
    donante_tipo: Literal["PF", "PM", "anonimo"]
    donante_rfc: str | None       # XAXX si anónimo
    donante_nombre: str
    monto_mxn: Decimal
    moneda_recibida: Literal["MXN", "USD", "EUR"]
    monto_origen: Decimal
    tc_aplicado: Decimal | None
    forma: Literal["transferencia", "tarjeta", "efectivo", "cheque", "especie"]
    fecha_recepcion: date
    proyecto_destino: str          # específico al objeto social
    cfdi_emitido: bool
    cfdi_uuid: str | None
    requiere_reporte_lfprh: bool   # si efectivo > $100k en mes
```

## 5. Skills propuestos (10)

| Skill | Cuándo activa |
|---|---|
| `dashboard-donataria` | Status mensual |
| `onboarding-donante-pf-pm` | Capturar nuevo donante |
| `cfdi-donativo-d04` | CFDI uso D04 |
| `reporte-mensual-efectivo-100k` | LFPRH si aplica |
| `declaracion-anual-transparencia` | Generar formato SAT |
| `tracking-ingresos-egresos` | Contabilidad simplificada |
| `remanente-distribuible-calc` | Cálculo art. 80 LISR |
| `renovacion-autorizacion-anual` | Alertas + documentación |
| `compliance-objeto-social` | Validar actividades vs autorización |
| `reporte-donativos-extranjero` | Si > $100k USD recibidos |

## 6. Comandos (6)

```
/donataria:dashboard
/donataria:donante
/donataria:cfdi
/donataria:reporte-mensual
/donataria:declaracion-anual
/donataria:renovacion
```

## 7. Workflow

`workflow-cierre-mensual-donataria.md`:
1. Cargar donativos del mes
2. Identificar reportables LFPRH (efectivo > $100k)
3. Emitir CFDIs D04 pendientes
4. Generar reporte ingresos/egresos
5. Calcular remanente distribuible parcial
6. Alertar si actividades fuera del objeto social
7. Persistir mes en histórico anual (para la transparencia)

## 8. Casos edge

| Caso | Acción |
|---|---|
| Donante PM con donativo $500k | CFDI D04 obligatorio; donante puede deducir 7% ingresos año anterior |
| Donante PF anónimo | XAXX010101000 — no deducible para donante |
| Donativo en especie (alimentos, libros) | Valuar a precio mercado + CFDI especie |
| Donativo en USD | Convertir a MXN con TC Banxico del día |
| Donataria que dejó de aparecer en Anexo 14 | NO emitir CFDI D04 hasta regularizar — donantes no podrán deducir |
| Remanente distribuible > 0 | Decidir destino (proyecto o reserva legal) |
| Actividad fuera del objeto social | Riesgo de perder autorización |
| Donativos provenientes del extranjero > $100k USD | Reporte CONDUSEF + SAT especializado |

## 9. Dependencias

- **MCPs**: `mp_facturama_extendido` (CFDI D04), `mp_sat_portal` (validación RFC donantes, consulta Anexo 14), `mp_banxico` (TC USD)
- **MCPs nuevos**: `mp_sat_anexo14_donatarias` (lista oficial — scrape mensual)
- **Skills `_shared/`**: cfdi-emision, rfc-validacion, mxn-formato, compliance-lfpdppp

## 10. Criterios de aceptación

- [ ] Plugin completo
- [ ] CFDI D04 emitido con todos los campos donataria
- [ ] Declaración informativa anual de transparencia generable
- [ ] Reporte mensual efectivo > $100k automatizado
- [ ] Tracking de remanente distribuible
- [ ] Alertas pre-renovación con 90 días
- [ ] Tests con 5 fixtures
- [ ] Lint passing

## 11. Esfuerzo estimado

- **Scaffold**: 5-10h
- **10 skills**: 100-160h
- **Workflow + reportes mensuales**: 40-60h
- **Generación declaración anual transparencia (formato SAT)**: 50-80h
- **Cálculo remanente distribuible**: 25-40h
- **Tests + 5 fixtures**: 30-50h
- **Docs + compliance**: 25-40h
- **Validación con contador especializado ONG**: 5-10h coordinación
- **TOTAL**: **280-450 horas** (~7-11 semanas FT)

## 12. Riesgos + mitigaciones

| Riesgo | Prob | Impacto | Mitigación |
|---|---|---|---|
| Donataria pierde autorización | Media | **CRÍTICO** | Tracker proactivo + alertas + checklist |
| Reportes LFPRH no presentados | Media | Alto | Cron mensual + alerta crítica |
| Reglas SAT cambian | Alta (anual) | Alto | Catálogo separado |
| Donativo del extranjero sin reportar | Baja | Alto | Detector automático |
| Datos donantes filtrados | Baja | Alto | Cifrado en reposo |

## 13. Decisiones pendientes

- [ ] ¿Integración con BlackBaud o Salesforce (CRM donantes profesional)?
- [ ] ¿Generación de carta deducibilidad personalizada al donante?
- [ ] ¿Pricing: $1,499 MXN/mes para donatarias pequeñas?

## 14. Plan de implementación

### Fase 1: Scaffold (5-10h)
### Fase 2: Donantes + CFDI D04 (50-80h)
### Fase 3: Reportes mensuales LFPRH (40-60h)
### Fase 4: Declaración anual transparencia (50-80h)
### Fase 5: Renovación autorización (25-40h)
### Fase 6: Tests + docs (50-80h)

## 15. Links

- [SAT - Donatarias Autorizadas](https://www.sat.gob.mx/minisitio/DonatariasAutorizadas/index.html)
- [SAT - Donativos deducibles](https://www.sat.gob.mx/minisitio/DeduccionesPersonales/donaciones.html)
- [Infobae - Nuevas reglas SAT donatarias 2026](https://www.infobae.com/mexico/2026/03/24/punto-por-punto-las-nuevas-reglas-del-sat-para-que-organizaciones-civiles-reciban-donativos/)
- [Facturando - Declaración SAT donatarias 2026](https://www.facturando.mx/blog/index.php/2026/06/01/donatarias-declaracion-sat-2026/)
- [Heru - Donativos deducibles SAT 2026](https://www.heru.app/blog/donativos-deducibles-sat-2026/)
- [Art. 79-82 LISR - Régimen donatarias](https://www.diputados.gob.mx/LeyesBiblio/pdf/LISR.pdf)
