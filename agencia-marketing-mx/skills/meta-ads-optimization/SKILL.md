---
name: meta-ads-optimization
description: Audita campañas de Meta Ads (Facebook + Instagram + Messenger + Audience Network) y propone optimizaciones específicas. Detecta fatiga creativa, audiencias saturadas, presupuesto mal distribuido, problemas de Pixel/CAPI/eventos, performance subóptimo de Advantage+ Campaign Budget, errores en eventos optimization, y oportunidades de escalado. Identifica creativos winners para "milking" antes de fatigarlos. Propone redistribución de presupuesto basada en mROAS y mCPA. Usar cuando el usuario diga optimizar Meta Ads, auditar Facebook Ads, revisar campañas Meta, mejorar performance, escalar Meta, fix Meta Ads, fatiga creativa, ad fatigue. NO usar para creación inicial de cuenta Meta (otro skill) ni para configuración técnica de Pixel/CAPI (skill técnico distinto).
allowed-tools: Read, Write, Edit
---

# Optimización de Meta Ads

Auditoría sistemática + recomendaciones priorizadas. No "consejos genéricos" sino acciones específicas con cifras del cliente.

## Checklist de auditoría — orden de prioridad

### 1. Tracking y eventos (CRÍTICO — si esto falla, todo lo demás es ruido)

- [ ] Meta Pixel instalado y firing en todas las páginas relevantes
- [ ] CAPI (Conversions API) activa con event matching > 5.0
- [ ] Deduplicación correcta entre Pixel y CAPI (mismo event_id)
- [ ] Eventos estándar correctos (Purchase, Lead, etc.) y con parámetros de valor/moneda (`currency: MXN`). Desde 2025 Meta ya no exige priorizar 8 eventos en Aggregated Event Measurement ni verificar dominio para configurar eventos (confianza media, fuente: Jon Loomer / reportes de la industria; confirmar en Events Manager)
- [ ] EMQ score > 7.0 (Event Match Quality, escala 0-10; umbral = heurística de agencia)
- [ ] Domain verification completada (sigue sirviendo para control de ediciones de links y marca)
- [ ] **Categoría del data source**: revisar en Events Manager si la cuenta quedó marcada como salud y bienestar u otra categoría restringida. Desde 2025 Meta limita la optimización a eventos de fondo de embudo (compra, cita) para esas marcas; en ese caso optimizar a eventos superiores y medir ventas fuera de Meta
- [ ] Customer information bien enviada (email hashed, phone hashed, fbp, fbc)

**Acción si falla**: detener cualquier optimización de creativo/audiencia y resolver tracking primero. Sin esto Meta optimiza ciego.

### 2. Estructura de cuenta

- [ ] BMA (Business Manager Account) con accesos correctos
- [ ] Cuenta publicitaria con método de pago vigente
- [ ] Ad sets no canibalizándose entre sí (mismo objetivo + mismas audiencias = canibalización)
- [ ] Naming convention consistente (sugerido: `<objetivo>_<audiencia>_<creativo-tipo>_<fecha>`)

### 3. Audiencias

- [ ] Custom Audiences segmentadas por LTV (visitantes web 30d, carritos abandonados, compradores 90d, lookalikes 1%/3%/5%)
- [ ] Lookalikes basados en eventos de fondo de funnel (compra), no top funnel (page view)
- [ ] Audiencias **no saturadas**:
  - Frequency promedio < 3.5 por audiencia
  - Reach < 60% de audiencia disponible
  - CPM no creciendo +30% vs últimos 30 días sin cambio
- [ ] **Advantage+ Audience** activado donde haga sentido (Meta sugiere audiences, AI decide)
- [ ] **Categorías especiales de anuncios** declaradas si aplica (crédito/servicios financieros, empleo, vivienda, temas sociales/electorales/políticos): limitan edad, género, ubicación y lookalikes. Si el cliente es fintech, inmobiliaria o reclutamiento, revisar antes de auditar audiencias
- [ ] Exclusiones bien configuradas (no mostrarle a compradores recientes ads de adquisición)

### 4. Creatividad

- [ ] Mínimo 4-6 creativos activos por ad set
- [ ] Diversidad de formato: imagen, video, carrusel, colección (cada ad set debería tener 2-3 formatos)
- [ ] Diversidad de hook (primeros 3 segundos del video, primer texto): 3-5 variaciones por concepto
- [ ] Aspect ratios: 9:16 para Reels/Stories (PRIORIDAD), 1:1 para feed, 4:5 para feed mobile-first
- [ ] Tiempos de video: <15 seg para Reels, 15-30 seg para feed
- [ ] CTAs claros y específicos ("Comprar ahora", "Aprovechar", "Ver detalles")
- [ ] **Fatiga creativa detectada en**:
  - CPM creciendo +20% en 14 días
  - CTR cayendo -30% en 14 días  
  - Frequency > 3.5 sostenida
- [ ] Refresh cadence: nuevos creativos cada 14-21 días en cuentas de alto presupuesto

### 5. Bidding y presupuesto

- [ ] Campaign Budget Optimization (CBO) activado para campañas con 3+ ad sets
- [ ] Campaña de ventas con Advantage+ (audiencia, presupuesto y ubicaciones en automático) probada vs estructura manual. Las antiguas Advantage+ Shopping Campaigns (ASC) se fusionaron en 2025-2026 en "Advantage+ sales campaigns"; la Marketing API v25.0 ya no permite crear ASC y en v26.0 las ASC existentes se pausan (fuente: Meta for Developers, 08-10-2025). Si el cliente aún tiene ASC, migrar duplicando desde Ads Manager
- [ ] Bidding: Lowest Cost para adquisición; Cost Cap o Bid Cap si hay target CPA específico
- [ ] **Learning phase**: ad sets que no salen de learning después de 7 días con 50+ optimization events necesitan cambio (creativo o audiencia)
- [ ] **Significant edits**: cambios de creativo/audiencia/budget de +20% resetean learning phase. Limitar.
- [ ] **Presupuesto mínimo viable**: el que permita ~50 eventos de optimización por semana por ad set (presupuesto diario ≈ CPA objetivo × 50 / 7). No hay un mínimo oficial fijo en MXN; Ads Manager muestra el mínimo de la cuenta

### 6. Optimization event

- [ ] Eventos de optimización son los correctos para el objetivo de negocio:
  - Ecommerce: Purchase (no Add to Cart)
  - Lead gen B2B: Lead form completion (no Page View)
  - App: App Install + Event (no solo Install)
- [ ] Si hay pocos eventos: optimizar por evento intermedio + filtro de calidad (ej. "Add to Cart" con filtro de scroll depth > 70%)

## Outputs estructurados

### Auditoría completa

```markdown
# Auditoría Meta Ads — [Cliente]
Fecha: [DD-MM-AAAA]
Periodo analizado: [últimos 30 días / mes específico]

## Score global: X/100

## Hallazgos críticos (resolver antes de cualquier optimización)
1. [Hallazgo 1] — Impacto estimado: [pérdida $/mes o oportunidad]
2. ...

## Hallazgos importantes (resolver en próximos 7 días)
1. ...
2. ...

## Oportunidades (mejora gradual)
1. ...
2. ...

## Plan de acción priorizado

### Semana 1
- [ ] Acción 1 (responsable: AM)
- [ ] Acción 2 (responsable: equipo creativo)

### Semana 2
- [ ] ...

## KPIs de seguimiento
- [Métrica 1]: actual vs target post-implementación
- ...
```

### Redistribución de presupuesto

Cuando el problema es allocation:

```
Campaña actual          Inversión actual    mROAS    mCPA    Recomendación
============================================================================
Adquisición core        $30,000             1.8x     $450    Bajar -20% ($24,000)
Retargeting 30d         $8,000              4.2x     $180    Subir +50% ($12,000)
LAL compradores         $12,000             2.5x     $320    Mantener
Catálogo (DPA)          $5,000              2.8x     $290    Mantener
[NUEVO] LAL LTV 90d     —                   —        —       Lanzar con $6,000

Total: $55,000 → $59,000 (+7.3%)
ROAS blended actual: 2.39x ($131,600 atribuido / $55,000)
ROAS proyectado: no se proyecta multiplicando ROAS promedio; el ROAS marginal
cae al escalar (sobre todo retargeting). Medir 14 días y comparar.
```

## Reglas de oro

1. **Una optimización a la vez**. Cambiar creativo + audiencia + presupuesto simultáneamente impide atribuir causa al efecto.
2. **No tocar lo que funciona**. Si un ad set tiene CPA 30% bajo target con learning estable, déjalo correr. Optimizar es para fixing, no para "movement".
3. **Esperar a learning phase** antes de juzgar. 7 días + 50 eventos mínimo.
4. **Tracking primero, creativo segundo, audiencia tercero**. Si tracking falla, lo demás no importa.
5. **Diversificar formatos pero no diluir**. 4-6 creativos por ad set con diversidad pero no 20 (Meta no aprende rápido).

## Insights operativos

- **Advantage+ sales campaigns** suelen competir bien contra setups manuales en ecommerce con catálogo amplio. Probar con test A/B, no asumir.
- **Reels** suele tener CPM más bajo que feed (la diferencia varía por cuenta; medir en el export). Aspecto 9:16 recomendado.
- **Conversion Lift studies** (cuando hay presupuesto > $50k MXN/mes) descubren campañas que parecen funcionar pero canibalizan orgánico.
- **Brand vs non-brand**: ROAS de search de marca está inflado por atribución; bajar 10-15% no afecta ventas reales.

## Datos que pide el skill

- Export CSV/XLSX de Ads Manager de los últimos 30+ días a nivel campaña, ad set y anuncio (columnas: inversión, impresiones, alcance, frecuencia, CPM, CTR, resultados, costo por resultado, valor de conversión). Este plugin **no** trae MCP de Meta Ads: no hay lectura en vivo de la cuenta; el usuario exporta o pega los datos
- Si el cliente factura la pauta en USD, `banxico_get_tc_dof` (MCP `banxico` del plugin) para convertir a MXN con el TC FIX/DOF de la fecha
- Tracking setup (Pixel ID, CAPI status, eventos prioritarios)
- Objetivo de negocio actual (escalado, defensiva, awareness, etc.)
- Target CPA/ROAS si existe
- Cualquier cambio reciente en producto/precio/landing

## Integración

- `reporte-mensual-cliente`: las recomendaciones de auditoría alimentan el reporte.
- `briefing-creativo`: cuando se requieren nuevos creativos, este skill arma el brief.
- `mxn-formato`: importes.
- `copy-mexicano`: revisar cumplimiento LFPC/COFEPRIS del copy antes de lanzar reemplazos.
