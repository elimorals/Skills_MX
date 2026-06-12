---
spec: "vertical-arrendador-residencial-mx"
estado: "DRAFT"
creado: "2026-06-11"
autor: "Elias"
ultima_actualizacion: "2026-06-11"
esfuerzo_estimado_horas: [280, 450]
prioridad: "tier-1"
---

# Spec 06 — Vertical `arrendador-residencial-mx`

## 1. Propósito

Vertical de **segundo mayor score (9.3/10)** — arrendadores residenciales en México. Mercado: ~2M arrendadores con 1-10 propiedades cada uno.

Resuelve los **dolores no resueltos** del arrendador típico:
1. Cobranza mensual recurrente sin convertirse en odiado por el inquilino
2. Screening de inquilinos potenciales (Buró + ingresos + referencias)
3. Contrato de arrendamiento conforme CCDF/CCF + actualización anual
4. CFDI mensual con uso D04 / S01 según regimen + deducibilidad para inquilino
5. Reportar ISR de arrendamiento (régimen 612 PF arrendamiento)
6. Tracking de mantenimiento + gastos deducibles
7. Manejo de problemas: inquilino que no paga, daños, vencimiento contrato

## 2. Contexto y por qué es novedoso

- **Lo que existe**: `inmobiliaria-mx` (vertical corredores e inmobiliarias — score 4.5/9). Tiene `contrato-arrendamiento-mx` y `screening-inquilinos`.
- **Por qué `inmobiliaria-mx` NO basta**: ese vertical es para **corredores/inmobiliarias** (los que conectan dueño + inquilino). El arrendador residencial es el **dueño directo** sin corredor intermedio.
- **Por qué es novedoso**: combina inmobiliaria + freelancers fiscal + cobranza + paciencia operativa de un caso particular (la relación dueño-inquilino es continua, no transaccional).
- **Diferencias clave vs inmobiliaria-mx**:
  - Foco en el dueño operando su propia propiedad
  - CFDI mensual de arrendamiento (régimen 612), no comisión de corredor
  - Cobranza directa (no via inmobiliaria)
  - Tracking de gastos deducibles (impuesto predial, mantenimiento)
  - Manejo emocional dueño-inquilino (relación de meses-años)

## 3. Alcance

**Dentro:**
- Plugin `arrendador-residencial-mx/` dedicado
- 7-9 skills propios
- 5-6 comandos slash
- Soporta hasta 10 propiedades por dueño
- Contratos PF arrendador → PF/PM inquilino
- Régimen fiscal 612 (arrendamiento) y 626 (RESICO PF)
- Cobranza escalada por nivel (similar a `freelancers-mx/cobranza-seguimiento` pero adaptada)

**Fuera (decisión deliberada):**
- Arrendamiento comercial (oficina, local) — caso aparte
- > 10 propiedades (es small landlord, no real estate empresa)
- Property management como servicio (eso es `inmobiliaria-mx` administración)
- Compraventa inmuebles (eso es corredores)
- Hipotecas / financiamiento — área específica

## 4. Inputs / outputs / schemas

### Setup inicial del arrendador

```python
class ArrendadorPerfil(BaseModel):
    rfc: str
    nombre: str
    regimen_fiscal: Literal["612_arrendamiento", "626_resico_pf"]
    propiedades: list[PropiedadInfo]
    cuenta_clabe_cobro: str
    email_cfdi: str
    tel_wa: str
```

### Propiedad

```python
class PropiedadInfo(BaseModel):
    id: str
    direccion: str
    cp: str
    municipio: str
    estado: str
    valor_catastral: Decimal | None
    cuenta_predial: str | None
    metros: int
    habitaciones: int
    banos: int
    renta_mensual: Decimal
    incremento_anual_inpc: bool  # vs porcentaje fijo
    porcentaje_fijo: float | None  # si no INPC
    fecha_proxima_actualizacion: date
    estado_ocupacion: Literal["vacante", "rentada", "remodelacion"]
    inquilino_actual_id: str | None
```

### Inquilino

```python
class Inquilino(BaseModel):
    id: str
    nombre: str
    rfc: str | None  # opcional si no quiere factura
    tel_wa: str
    email: str
    propiedad_id: str
    fecha_inicio_contrato: date
    fecha_fin_contrato: date
    renta_mensual_mxn: Decimal
    deposito_garantia_mxn: Decimal
    fiador: dict | None
    historial_pagos: list[Pago]
    historial_comunicaciones: list[Mensaje]
```

## 5. Skills propuestos (8)

| Skill | Cuándo activa |
|---|---|
| `dashboard-propiedades` | Status mensual: pagadas, vencidas, vacantes |
| `screening-inquilino-completo` | Pipeline: solicitud → docs → Buró → referencias → decisión |
| `contrato-arrendamiento-residencial` | Genera contrato CCDF/CCF + adendums |
| `cobranza-mensual-renta` | Cobranza escalada con tono adecuado a relación continua |
| `cfdi-arrendamiento-mensual` | CFDI tipo I uso D04 (uso casa-habitación) o I uso G03 |
| `actualizacion-renta-anual` | INPC o porcentaje fijo + comunicación al inquilino |
| `gastos-deducibles-propiedad` | Track predial, mantenimiento, reparaciones, agua, IVA acreditable |
| `cierre-contrato-checklist` | Inspección final, devolución depósito, prorroga vs no, nuevo inquilino |

## 6. Comandos propuestos (5)

```
/arrendador:dashboard            # Ver status de todas las propiedades
/arrendador:screening            # Evaluar inquilino candidato
/arrendador:contrato             # Generar contrato nuevo
/arrendador:facturar-mes         # Emitir CFDIs del mes a todos los inquilinos
/arrendador:cobranza             # Corrida de cobranza escalada para morosos
```

## 7. Workflow orquestador (1)

`workflow-cobranza-renta-mensual` — para un mes:
1. Identificar propiedades rentadas
2. Para cada una: ¿hay pago confirmado del mes?
3. Si no: nivel de escalamiento (D+3, D+7, D+15, D+30)
4. Mandar WhatsApp + email apropiado
5. Si D+30: marca para iniciar proceso desalojo
6. Reporte final

## 8. Casos edge

| Caso | Comportamiento |
|---|---|
| Inquilino paga depositando directo a cuenta sin avisar | Detectar via cruce bancario + auto-marcar pagado |
| Inquilino pide factura tarde (depués de mes corriente) | Emitir CFDI con fecha del mes facturado, no actual |
| Renta incrementada según INPC pero inquilino se opone | Plantilla legal + opciones (mantener vs cambio inquilino) |
| Daños mayores al inmueble | Inspección + deducir depósito + protocolo escalación |
| Inquilino con familiar dependiente / niños (vulnerable) | Cobranza con tono extra cuidadoso |
| Vacante prolongada (> 60 días) | Sugerencias: bajar renta, mejorar foto, agregar amenidades |
| Inquilino pierde empleo y no puede pagar | Plan de pago + plazo gracia (decisión del dueño) |
| Contrato vence y nadie habla | Proactividad: notificar 60 días antes |
| Cancelación de RFC del inquilino (mudanza al extranjero) | CFDI genérico XAXX (no deducible) |

## 9. Dependencias

- **MCPs**: `mp_facturama_extendido` (CFDI), `mp_banxico` (TC + INPC), `mp_buro_credito_personal` (screening con autorización), `mp_bancos_mx` (cruce pagos), `mp_inmuebles24` (comparables zona para pricing), `mp_sat_portal` (status RFC inquilino)
- **Plugins relacionados**: usa skills de `inmobiliaria-mx` (`contrato-arrendamiento-mx`, `screening-inquilinos`, `comparables-zona`) — opcionalmente como dependencia o copia
- **Skills `_shared/`**: cfdi-emision, iva-retenciones-mx, rfc-validacion, whatsapp-business-mx, compliance-lfpdppp, mxn-formato

## 10. Criterios de aceptación

- [ ] Plugin completo con 8 skills + 5 commands
- [ ] Dashboard funciona con 1-10 propiedades
- [ ] Screening con Buró requiere autorización formal (compliance)
- [ ] Contratos generados con cláusulas vigentes CCDF/CCF
- [ ] CFDI mensual emite con uso D04 (residencial) o G03 (cliente PM oficina rentando habitación)
- [ ] Actualización INPC anual automática con notificación
- [ ] Tracking de gastos deducibles para declaración anual
- [ ] Cobranza escalada con tono apropiado (no quemar relación)
- [ ] Lint passing
- [ ] Tests con 5 fixtures (5 escenarios típicos)
- [ ] Integrable con `pf-anual-mx` para declaración

## 11. Esfuerzo estimado

- **Scaffold plugin + plugin.json**: 5-10h
- **8 skills SKILL.md + references**: 100-150h (~12-18h/skill)
- **5 comandos**: 15-25h
- **Workflow cobranza-renta-mensual**: 20-40h
- **Dashboard + tracking propiedades**: 30-50h
- **Generación contratos PDF**: 20-30h
- **Cruce bancario automático (vía `mp_bancos_mx`)**: 30-50h
- **Tests + fixtures (10+)**: 35-60h
- **Docs + guía vertical**: 20-30h
- **Validación legal con abogado mercantilista (no codificable)**: 5-10h coordinación
- **TOTAL**: **280-455 horas** (~7-12 semanas FT)

⚠ Para score 7.5/9 (producción-grade) requiere validación legal con abogado especializado en arrendamiento (~$5-12k MXN consultoría).

## 12. Riesgos + mitigaciones

| Riesgo | Prob | Impacto | Mitigación |
|---|---|---|---|
| Cláusulas contrato no válidas en estado específico | Media | Crítico | Validar por estado + warning "consulta abogado tu estado" |
| Cobranza muy agresiva = pierde inquilino bueno | Media | Alto | Templates con tono adaptado al histórico del inquilino |
| Datos del inquilino expuestos (LFPDPPP) | Baja | Alto | Aviso privacidad obligatorio + cifrado de datos sensibles |
| Cambio INPC anual no aplicado correctamente | Baja | Medio | Catálogo INEGI vigente + validación |
| Buró consultado sin autorización (delito) | Baja | **Crítico** | Schema Pydantic exige token autorización (igual mp_buro_credito_personal) |
| Inquilino violenta y dueño en peligro | Baja | Alto | Protocolo escalación a autoridades + asesoría legal |
| Desalojo legal complejo CDMX vs estados | Alta | Alto | Documentar variaciones por estado + sugerir abogado local |

## 13. Decisiones pendientes

- [ ] ¿Producto B2C ($199 MXN/mes por dueño hasta 5 propiedades) vs B2B (white-label inmobiliarias)?
- [ ] ¿Incluir tour virtual de propiedades vacantes para acelerar renta?
- [ ] ¿Integración con CFE/agua para monitorear consumo (detectar habitación informal)?
- [ ] ¿Score crediticio dinámico del inquilino (alerta si Buró cambia mid-contrato)?
- [ ] ¿Compartir referencias entre arrendadores red (privacy concern)?

## 14. Plan de implementación

### Fase 1: Scaffold + plugin base (10-15h)
1. `arrendador-residencial-mx/.claude-plugin/plugin.json`
2. README + CHANGELOG
3. Estructura carpetas
4. Sync `_shared/` + copia skills relevantes de `inmobiliaria-mx`

### Fase 2: Skills básicos de captura (40-60h)
1. `dashboard-propiedades/SKILL.md`
2. `screening-inquilino-completo/SKILL.md` (con compliance Buró)
3. `cobranza-mensual-renta/SKILL.md` (5 niveles escalación)

### Fase 3: Skills fiscales y de contrato (40-60h)
4. `contrato-arrendamiento-residencial/SKILL.md`
5. `cfdi-arrendamiento-mensual/SKILL.md`
6. `gastos-deducibles-propiedad/SKILL.md`

### Fase 4: Skills de operación continua (30-50h)
7. `actualizacion-renta-anual/SKILL.md`
8. `cierre-contrato-checklist/SKILL.md`

### Fase 5: Comandos + workflow (35-65h)
1. 5 commands
2. `workflow-cobranza-renta-mensual`
3. Cruce bancario automático

### Fase 6: Tests + fixtures (35-60h)
1. 10 fixtures (escenarios típicos + edge)
2. Tests unitarios + integración

### Fase 7: Docs + validación legal (25-40h)
1. `docs/guia-vertical-arrendador-residencial.md`
2. Coordinación con abogado especializado
3. Update STATUS.md

## 15. Links

- Research original: score 9.3/10
- `inmobiliaria-mx` actual: tiene skills aprovechables
- Código Civil CDMX Art. 2398-2496 (arrendamiento)
- INEGI INPC mensual: https://www.inegi.org.mx/temas/inpc/
- Marco legal LFPC arrendamiento: Art. 17, 18
