# Roadmap — visión 12 meses

**Propósito**: dirección del monorepo a 12 meses, prioridades, y nuevos verticales en pipeline.

**Audiencia**: stakeholders, contribuyentes potenciales, partners.

**Pre-lectura**: [estado-real.md](estado-real.md), [plan-afinacion.md](plan-afinacion.md).

---

## Estado a hoy (2026-06-11)

- 5 plugins scaffoldeados (core-mexico + 4 verticales)
- 54 skills lint-passing
- Score promedio honesto: 4.7/9 (scaffolding denso, no producción)
- Documentación: ~20 archivos en docs/
- Tooling: sync, lint, evals, fixtures
- Cero validaciones expertas
- Cero integraciones reales activadas

---

## Q3 2026 (jul-sep): freelancers-mx a producción

### Hitos
- Dogfooding con 3-5 clientes reales propios
- Contador certificado valida `freelance-tax-mx`
- Abogado mercantilista valida contratos
- Facturama sandbox conectado + 100+ CFDIs de prueba exitosos
- Score freelancers-mx ≥ 7.5/9
- Lanzamiento como producto interno

### Métricas a alcanzar
- Tiempo en cotización: < 15 min
- CFDIs sin error: > 99%
- Cartera vencida personal: < 10%

---

## Q4 2026 (oct-dic): agencia-marketing-mx a producción + ecommerce-mx scaffold

### Hitos agencia-marketing-mx
- 1 partner senior CM validando templates
- 1 partner performance marketer validando checklist
- 3-5 templates WhatsApp aprobados por Meta real
- Score ≥ 7.5/9

### Hitos ecommerce-mx
- Scaffold completo con 5 skills:
  - `mercado-libre-listings`
  - `mercado-libre-pricing`
  - `shopify-mx`
  - `inventario-multicanal`
  - `paqueteria-mx`
- MCP server custom para Mercado Libre (no existe oficial)
- Integración con Shopify (existe MCP)

### Primer cliente externo pagado
- Para freelancers-mx: implementación a freelancer de tu red
- Precio piloto: $30k-50k MXN

---

## Q1 2027 (ene-mar): talleres-mx a producción + colegios-mx con partner

### Hitos talleres-mx
- Partner dueño de taller (preferible CDMX/Monterrey/GDL)
- Abogado defensa del consumidor revisa certificado de garantía
- Operación real 3-4 meses
- Bitácora WhatsApp con 100+ autorizaciones documentadas
- Score ≥ 7.5/9

### Hitos colegios-mx
- Partner indispensable: directora administrativa de colegio K-12
- Contador especializado en educación
- Abogado educativo
- Primera emisión real de CFDI D10 con InsEduc

---

## Q2 2027 (abr-jun): colegios-mx a producción + nuevos verticales

### Hitos colegios-mx
- 1 ciclo escolar completo operado en paralelo
- 200+ CFDIs emitidos sin error
- Comunicación masiva con padres operando
- Score ≥ 7.5/9

### Nuevos verticales scaffold
- **salon-mx**: spas, salones, estéticas premium
- **veterinaria-mx**: clínicas y pet care
- **wedding-mx**: wedding planners
- **restaurante-mx**: dark kitchens + restaurantes pequeños

### Tooling avanzado
- CI/CD para lint automático en cada PR
- `scripts/run-fixtures.sh` automatizado
- Dashboard de salud del monorepo (score por skill)
- Calibrador de descriptions integrado (replica de skill-creator)

---

## Q3 2027 (jul-sep): consolidación y skills standalone

### Hitos
- Empaquetado de skills propios como standalone (skillkit)
- Distribución dual: plugins para uso enterprise + skills para uso individual
- 4-5 verticales con scoring ≥ 7.5/9
- 5-10 clientes externos pagados activos
- $200k-500k MXN MRR del negocio de implementación

### Posicionamiento
- Marketplace privado bajo Anthropic
- Caso de uso documentado de cada vertical
- Presencia en LinkedIn / blog / podcasts mexicanos de tech

---

## Q4 2027 (oct-dic): expansión

### Verticales adicionales en pipeline
- **inmobiliaria-mx**
- **despacho-legal-mx**
- **clinica-salud-mx** (con socio médico)
- **constructora-mx** (Carta Porte intensivo)
- **agente-seguros-mx**

### LATAM exploration
- Investigación de mercado Colombia, Chile, Argentina
- Posible monorepo paralelo `plugins-co`, `plugins-ar` con base reutilizable

### Comunidad
- Discord/Slack de usuarios
- Tutoriales en video
- Caso de estudio público (con clientes que autoricen)

---

## Q1 2028+: visión a 2+ años

### Posibles evoluciones
- **Versión SaaS**: para clientes que no quieren operar Claude Code (con UI web)
- **API publica**: para que otros sistemas consuman skills via API
- **Marketplace público en Anthropic**: distribución masiva con pricing freemium
- **Certificación de skills**: programa de "validado por expertos" con badge

---

## Métricas de éxito del monorepo (12 meses)

| Métrica | Hoy | Target Q3 2026 | Target Q1 2027 | Target Q4 2027 |
|---|---|---|---|---|
| Verticales en producción | 0 | 1 | 3 | 4-5 |
| Verticales scaffoldeados | 4 | 4 | 5 | 8-10 |
| Skills totales | 54 | 60 | 75 | 100+ |
| Score promedio honesto | 4.7/9 | 5.5/9 | 6.5/9 | 7.5/9 |
| Clientes externos pagados | 0 | 1 | 3-5 | 8-15 |
| MRR | $0 | $10k MXN | $50k-150k MXN | $200k-500k MXN |
| Partners del sector | 0 | 1 | 3 | 5-8 |
| Templates WhatsApp aprobados Meta | 0 | 3-5 | 10-15 | 25+ |
| CFDIs emitidos en producción | 0 | 100+ | 1000+ | 5000+ |

---

## Decisiones pendientes (a tomar pronto)

### 1. Open source vs privado
**Hoy**: directorio local privado.
**Próximo paso**: decidir si publicar en GitHub público para tracción/comunidad o mantener privado para control.

### 2. Branding del marketplace
- "Plugins MX" (descriptivo)
- "Brand propio" (ej. "Cipre Plugins", "Ops MX")
- "Co-branded con Anthropic" (si hay acuerdo)

### 3. Modelo de negocio
- **Modelo A**: cobrar implementación + retainer mensual (alta gama)
- **Modelo B**: marketplace público con freemium (volumen)
- **Modelo C**: híbrido — open source con servicios pagados

### 4. Estructura legal del negocio
- Si crece más allá de freelance, considerar SA de CV o SAS
- Si hay socios sector, contratos claros

---

## Riesgos del roadmap

| Riesgo | Probabilidad | Mitigación |
|---|---|---|
| Competidor copia tesis y va más rápido | Media | Velocidad de afinación con partners |
| Anthropic cambia política de plugins | Baja-media | Skills standalone como fallback |
| SAT/INAI cambian regulación → re-escritura | Alta (siempre pasa) | Mantenimiento como parte de modelo |
| Cliente piloto tiene mal experiencia y daña reputación | Media | Validación obsesiva antes de exponer |
| Falta de tiempo / quema | Alta | Ritmo sostenible, no burnout |

---

## Cómo medir si el roadmap funciona

Cada trimestre revisar:
1. ¿Cumplimos el hito principal? Sí/No.
2. ¿Score mejoró según target?
3. ¿MRR creció?
4. ¿Conseguimos los partners planeados?
5. ¿Ningún incidente regulatorio?

Si 4 de 5: estás bien. Si 2-3: ajustar. Si 0-1: re-evaluar tesis.

---

## Ver también

- [estado-real.md](estado-real.md) — estado actual honesto
- [plan-afinacion.md](plan-afinacion.md) — plan táctico semana a semana
- [INDEX.md](INDEX.md) — índice general
