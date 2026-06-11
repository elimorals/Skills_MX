# Métricas — KPIs por vertical y por skill

**Propósito**: qué medir para saber si el monorepo está entregando valor.

**Audiencia**: usuarios finales y stakeholders.

**Pre-lectura**: [estado-real.md](estado-real.md).

---

## Métricas del monorepo

### Salud del código

| Métrica | Target | Cómo medir |
|---|---|---|
| Lint passing | 100% | `./scripts/lint-skills.sh` |
| Cobertura de fixtures | > 60% de skills con fixture | Contar archivos en `tests/fixtures/` |
| Cobertura de evals | > 80% de skills con eval | Contar archivos en `evals/` |
| Score promedio honesto | > 7.0/9 | Auditar [estado-real.md](estado-real.md) |

### Salud del producto

| Métrica | Target |
|---|---|
| Plugins en producción | 4+ |
| Verticales scaffoldeados | 8+ |
| Templates WhatsApp aprobados | 25+ |
| Catálogos SAT validados vigentes | 100% |

---

## Métricas por vertical

### freelancers-mx

#### Operacionales (lo que el usuario nota)

| Métrica | Target | Cómo medir |
|---|---|---|
| Tiempo en cotización | < 15 min | Cronometrar |
| Tiempo en cobranza al mes | < 2 hrs | Sumar interacciones |
| % cotizaciones cerradas | > 30% | Pipeline JSON |
| Cartera vencida | < 15% | Sumar adeudos / facturación |
| Días promedio cobro | < 30 días | Promedio facturas pagadas |
| CFDIs sin error | > 99% | Bitácora cancelaciones |
| Pago provisional sin diferencia con contador | > 95% | Comparar |

#### De valor entregado

| Métrica | Valor |
|---|---|
| Horas ahorradas/semana | 8-12 |
| Equivalente económico (tarifa $600/hr) | $4,800-$7,200/semana |
| Tiempo en estrategia + venta vs admin | 70/30 con plugin vs 40/60 sin |

### agencia-marketing-mx

#### Operacionales

| Métrica | Target |
|---|---|
| Tiempo en reporte mensual por cliente | < 1 hr |
| Tiempo en respuestas CM | < 30 min en horario hábil |
| % auditorías que detectan oportunidad accionable | > 90% |
| Templates aprobados primer intento Meta | > 70% |
| Quality Rating WA cuentas gestionadas | GREEN |

#### De valor entregado

| Métrica | Valor |
|---|---|
| Horas ahorradas AM/semana | 30+ |
| AM puede gestionar +2-3 cuentas | +$50k-$150k MRR/AM |
| Mejora promedio ROAS post-auditoría | +15-30% |

### colegios-mx

#### Operacionales

| Métrica | Target |
|---|---|
| Cartera vencida | < 8% (vs 18% nacional) |
| Tiempo admin en cobranza/mes | < 10 hrs (vs 25-40) |
| % CFDIs deducibles emitidos correctamente | > 99% |
| Tasa respuesta WhatsApp masivo | > 85% |
| Constancias generadas sin error | > 99% |
| Reclamos PROFECO al año | 0 |

#### De valor entregado

| Métrica | Valor para colegio de 300 alumnos |
|---|---|
| Reducción cartera vencida 18% → 8% | +$300k-600k MXN/año |
| Tiempo admin liberado | 60-100 hrs/mes |
| CFDIs deducibles correctamente | menos quejas de padres |

### talleres-mx

#### Operacionales

| Métrica | Target |
|---|---|
| % cotizaciones cerradas | > 60% |
| Tiempo cotización → autorización | < 4 hrs hábiles |
| Días promedio auto en taller | < 2 |
| Reclamos de garantía / total OTs | < 5% |
| Reclamos PROFECO al año | 0 |
| CFDIs emitidos al cierre | > 80% |

#### De valor entregado

| Métrica | Valor para taller mediano |
|---|---|
| % cotizaciones cerradas: 40% → 60% | +50% revenue |
| Reducción tiempo administrativo | 15-25 hrs/semana |
| Defensa PROFECO sólida | 0 multas |

---

## Métricas técnicas

### Performance del sistema

| Métrica | Target | Cómo medir |
|---|---|---|
| Tiempo de carga de plugin | < 2 seg | Cronometrar startup |
| Tiempo de respuesta a comando | < 30 seg típico | Cronometrar /comando |
| Tokens por interacción promedio | < 10k | Logs de Claude |
| Errores en timbrado | < 1% | Bitácora PAC |

### Calidad de calibración (cuando se aplique)

| Métrica | Target |
|---|---|
| Accuracy de eval por skill | > 85% |
| False positives (over-triggering) | < 10% |
| False negatives (under-triggering) | < 10% |

---

## Métricas de impacto al cliente

### Para freelancer / consultor

Antes vs después de adoptar el plugin (3 meses):

| Métrica | Antes (típico) | Después (target) |
|---|---|---|
| Horas administrativas/semana | 15-20 | 5-8 |
| Cotizaciones enviadas/mes | 5-10 | 10-20 |
| % cerradas | 25-35% | 35-50% |
| Cartera vencida | 15-25% | < 10% |
| Errores en CFDI/mes | 1-3 | 0-1 |
| Stress autoreportado (1-10) | 7-9 | 4-6 |

### Para agencia

Por AM (3 meses):

| Métrica | Antes | Después |
|---|---|---|
| Cuentas que gestiona | 5-8 | 8-12 |
| Horas/semana en reportes | 15-25 | 5-10 |
| Horas/semana en estrategia | 5-10 | 15-25 |
| CSAT cliente | 6-7/10 | 8-9/10 |

### Para colegio (300 alumnos)

| Métrica | Antes (típico nacional) | Después |
|---|---|---|
| Cartera vencida | 18% promedio | < 8% |
| Tiempo cobranza admin/mes | 30-50 hrs | < 12 hrs |
| Quejas de padres por mal CFDI | 5-15/año | 0-2/año |
| Tiempo en constancias | 30-60 min c/u | 5-10 min c/u |

### Para taller (5-10 servicios/día)

| Métrica | Antes | Después |
|---|---|---|
| % cotizaciones cerradas | 35-45% | > 60% |
| Tiempo cotización → autorización | 1-3 días | <4 horas hábiles |
| Días promedio auto en taller | 3-5 | < 2 |
| Disputas de cobro | 1-3/mes | 0-1/mes |

---

## Métricas de negocio (para ti)

### Si vendes implementación

| Métrica | Q3 2026 | Q1 2027 | Q4 2027 |
|---|---|---|---|
| Clientes externos pagados | 1 | 3-5 | 8-15 |
| MRR ($MXN) | 10k | 50k-150k | 200k-500k |
| LTV promedio cliente | $50k-150k | $100k-200k | $150k-300k |
| Churn anual | < 20% | < 15% | < 10% |
| CAC | mucho (referidos manuales) | $5k-15k | $15k-30k |

### Adopción del monorepo (si publicas)

| Métrica | Año 1 | Año 2 |
|---|---|---|
| Forks/stars (si público) | 50-200 | 500-2000 |
| Plugins instalados/mes | 100 | 1000+ |
| Partners colaboradores | 1-2 | 5-10 |
| Skills standalone descargados | 200/mes | 2000+/mes |

---

## Métricas de compliance

| Métrica | Target |
|---|---|
| Multas SAT al año | 0 |
| Multas INAI al año | 0 |
| Multas PROFECO al año | 0 |
| Solicitudes ARCO en plazo | 100% |
| Vulneraciones de datos reportadas | 0 (idealmente) |
| Auditorías SAT con resultado favorable | 100% |

---

## Cómo trackear

### Bitácoras automáticas

Cuando un skill ejecuta, debe registrar en `audit-log/<vertical>/<YYYY-MM>.jsonl`:

```jsonl
{"timestamp": "...", "skill": "cfdi-emision", "outcome": "success", "uuid": "abc-...", "cliente_anonimo_id": "hash123"}
{"timestamp": "...", "skill": "cobranza-seguimiento", "outcome": "etapa_2_enviada", "cliente_anonimo_id": "hash456"}
```

Cada 30 días, agregar:
- Total operaciones por skill
- Tasa de éxito
- Tasa de error con tipo

### Reportes manuales

Cada cierre de mes, registrar en `reports/<vertical>/YYYY-MM.md`:
- KPIs operacionales
- KPIs de impacto observados
- Lecciones aprendidas

---

## Dashboards futuros

Por implementar (no hoy):
- Dashboard agregado en Looker Studio / Grafana
- Scoring automático contra checklist 9 puntos
- Alertas si métricas se degradan

---

## Ver también

- [estado-real.md](estado-real.md) — score honesto actual
- [plan-afinacion.md](plan-afinacion.md) — milestones para mejorar
- [compliance-checklist.md](compliance-checklist.md) — qué documentar
