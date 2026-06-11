---
name: reporte-mensual-cliente
description: Genera reporte mensual ejecutivo de marketing digital para clientes de agencia. Estructura KPIs por canal (Meta Ads, Google Ads, TikTok Ads, GA4, redes orgánicas), comparativo vs mes anterior y vs benchmark del cliente, insights accionables, top winners y top losers, próximos pasos del mes siguiente, y storytelling ejecutivo que un CMO no técnico pueda leer en 3 minutos. Salida en formato presentable (Google Slides export friendly, Looker Studio integration ready). Usar cuando el usuario diga reporte mensual, monthly report, report cliente, dashboard mensual, KPIs del mes, performance review, marketing report, fin de mes, cierre mensual. NO usar para reportes en tiempo real (dashboards live, no estáticos).
allowed-tools: Read, Write, Edit, Bash
---

# Reporte mensual ejecutivo para cliente de agencia

El AM típico tarda 4-6 horas armando este reporte. Bien estructurado se baja a 30-60 minutos: el AM dedica el tiempo a interpretar, no a copiar/pegar números.

## Estructura del reporte

```markdown
# [Cliente] — Reporte de Marketing
## [Mes] [Año]

Preparado por: [Agencia / AM]
Fecha: [DD de mes de AAAA]

---

## 1. Resumen ejecutivo

[3-5 líneas. Lo único que el CEO lee.]

- **Resultado clave del mes**: [una frase potente]
- **Inversión total**: $XXX,XXX MXN (vs mes anterior +/-Y%)
- **Conversiones**: N (vs benchmark Z%)
- **CPA blended**: $XXX MXN (vs target Z%)
- **Highlight**: [logro destacado]
- **Foco siguiente mes**: [qué viene]

---

## 2. KPIs principales

### 2.1 Performance global

| Métrica | Este mes | Mes anterior | Variación | vs Target |
|---|---|---|---|---|
| Inversión | $XXX,XXX | $XXX,XXX | ±X% | ✓/✗ |
| Impresiones | X,XXX,XXX | X,XXX,XXX | ±X% | — |
| Clicks / Sesiones | XX,XXX | XX,XXX | ±X% | — |
| CPM | $XX.XX | $XX.XX | ±X% | — |
| CPC | $X.XX | $X.XX | ±X% | — |
| CTR | X.X% | X.X% | ±X% | — |
| Conversiones | XXX | XXX | ±X% | ✓/✗ |
| CPA | $XXX | $XXX | ±X% | ✓/✗ |
| ROAS | X.XX | X.XX | ±X% | ✓/✗ |

### 2.2 Por canal

| Canal | Inversión | Conversiones | CPA | ROAS |
|---|---|---|---|---|
| Meta Ads | $XX,XXX | XX | $XXX | X.XX |
| Google Ads | $XX,XXX | XX | $XXX | X.XX |
| TikTok Ads | $XX,XXX | XX | $XXX | X.XX |
| Orgánico | — | XX | — | — |
| **Total** | **$XXX,XXX** | **XXX** | **$XXX** | **X.XX** |

---

## 3. Análisis por canal

### 3.1 Meta Ads
- **Top campaigns**: [3 mejores]
- **Bottom campaigns**: [3 peores con razón]
- **Creative fatigue detectada**: [creativos con CPM creciente y CTR decreciente]
- **Audiencias saturadas**: [audiencias con frecuencia >3.5 que ya no escalan]
- **Aprendizajes**: [lo que funcionó/no funcionó]

### 3.2 Google Ads
- **Search performance**: keywords top, gasto en términos de marca vs no-marca
- **Performance Max**: si aplica, performance vs Search clásico
- **Negative keywords agregadas**: cuántas y impacto estimado

### 3.3 TikTok Ads (si aplica)
- **Spark Ads vs creativos propios**: comparativo
- **Smart+ vs manual**: comparativo
- **Hooks de mejor performance**: descripción

### 3.4 Orgánico (si aplica)
- Crecimiento de seguidores
- Engagement rate
- Contenidos top de cada red

---

## 4. Insights accionables

[3-5 hallazgos clave con recomendación específica]

**1. [Hallazgo]**
- Lo que vemos: [datos]
- Lo que implica: [hipótesis]
- Lo que recomendamos: [acción específica]

**2. [Hallazgo]** ...

---

## 5. Top winners del mes

[2-3 cosas que funcionaron particularmente bien — para celebrar y replicar]

## 6. Top losers del mes

[2-3 cosas que no funcionaron — para corregir]

---

## 7. Próximos pasos (mes siguiente)

| Acción | Owner | Deadline | Inversión estimada |
|---|---|---|---|
| [Acción 1] | [Agencia/Cliente] | [Fecha] | $XX,XXX |
| [Acción 2] | ... | ... | ... |

---

## 8. Anexos

- Detalle de campañas en Looker Studio / Data Studio: [link]
- Screenshots de creativos top: [link]
- Detalle de audiencias y segmentos: [link]
```

## Lo que hace este skill

1. **Pide al usuario las métricas brutas** o lee de archivos (CSV exportado de plataformas, JSON de API).
2. **Estructura el reporte** según el formato anterior, adaptándolo al cliente (eliminando secciones N/A).
3. **Calcula variaciones** vs mes anterior automáticamente.
4. **Genera insights** marcando hallazgos importantes (anomalías estadísticas, fatiga creativa, etc.).
5. **Sugiere próximos pasos** basados en patrones de datos.
6. **Output en markdown** convertible a Google Slides, PDF, o documento ejecutivo.

## Reglas de detección automática

### Fatiga creativa Meta
- Frequency > 3.5 sostenida 7+ días → marcar candidato a refresco
- CPM creciendo +20% en 14 días con creativo sin cambio → fatiga
- CTR cayendo -30% sin cambio de audiencia → fatiga

### Audiencias saturadas
- Audiencia core con reach > 70% del tamaño estimado → saturada
- Custom Audience con > 60% de penetración → saturada

### Términos de marca vs no-marca en Search
- Si gasto en términos de marca > 30% del total Search: alerta para revisar (canibalización SEO/PPC, atribución inflada)

### CPA escalando
- CPA mensual creciendo >15% vs los últimos 3 meses sin ajuste de target → revisar

## Tono del reporte

**Para el cliente**: ejecutivo, claro, con cifras. Cero jargon innecesario. Reemplazar:
- "CTR" → "tasa de clicks"
- "CPM" → "costo por mil impresiones"
- "ROAS" → "retorno por peso invertido"

**Excepción**: si el cliente es marketero (CMO con background) puede usar jargon estándar.

## Datos que pide el skill

- Período (mes/año)
- Cliente
- Canales activos (Meta, Google, TikTok, otros)
- Métricas brutas: opción A) export CSV de cada plataforma; opción B) input manual estructurado
- Goals/targets del cliente para comparar
- Cualquier nota cualitativa: campañas lanzadas, eventos del cliente, cambios en producto

## Outputs

1. Reporte markdown completo en `reportes/[cliente]/YYYY-MM.md`.
2. Versión ejecutiva 1 página (solo secciones 1 y 4) en `reportes/[cliente]/YYYY-MM-resumen.md`.
3. Lista de assets faltantes si no tienes todo lo necesario.

## Integración

- Puede consumir export de Meta Ads Manager (CSV), Google Ads Editor (CSV), TikTok Ads (XLSX).
- Cuando exista MCP de Meta/Google/TikTok activo, jala datos en vivo.
- `mxn-formato` para todos los importes.
