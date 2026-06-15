# Guía vertical: agencia-marketing-mx

**Propósito**: cómo usar el plugin para agencias de marketing digital.

**Audiencia**: account managers, dueños de agencia, performance marketers.

**Pre-lectura**: [guia-instalacion.md](guia-instalacion.md).

---

## Para quién es este plugin

- Agencia digital con 5-25 personas (o consultor unipersonal con 5+ cuentas)
- Facturación $200k-$2M MXN/mes
- Maneja Meta Ads, Google Ads, TikTok Ads, GA4
- Atiende 5-25 cuentas activas

---

## Skills propios

| Skill | Propósito |
|---|---|
| `reporte-mensual-cliente` | Reporte ejecutivo con KPIs por canal |
| `meta-ads-optimization` | Auditoría 6 áreas + plan priorizado |
| `copy-mexicano` | Copy que evita "español neutro" |
| `community-management-mx` | Respuestas con tono de marca, escalación |
| `briefing-creativo` | Brief estructurado con audiencia con insight |

---

## Commands

- `/agencia:reporte <cliente> <mes>` — reporte mensual ejecutivo
- `/agencia:auditoria-cuenta <cliente>` — auditoría Meta Ads
- `/agencia:copy <canal> <contexto>` — copy publicitario
- `/agencia:brief <cliente> <proyecto>` — brief creativo

---

## Flujos operativos típicos

### Flujo 1: Cierre mensual de reportes (lunes primero del mes)

```
Usuario: "Necesito los reportes de marzo para mis 6 clientes."

Claude → Para cada cliente:
        1. /agencia:reporte <cliente> marzo-2026
        2. Pide o lee CSV de Meta/Google/TikTok
        3. Calcula variaciones vs feb, vs target
        4. Detecta winners/losers
        5. Genera reporte.md + resumen-1pag.md
        6. Sugiere conversión a Slides

Output: 6 reportes en reportes/<cliente>/2026-03.md listos.
Tiempo total: ~45 min vs 4-6h manualmente.
```

### Flujo 2: Auditoría de cuenta nueva

```
Usuario: "Acaba de firmar Cinepolis, necesito auditar su cuenta Meta antes de
        proponerles plan."

Claude → /agencia:auditoria-cuenta cinepolis
        Pide CSV últimos 30 días + setup Pixel/CAPI.
        
        Aplica checklist 6 áreas:
        1. Tracking (Pixel + CAPI + eventos)
        2. Estructura de cuenta
        3. Audiencias
        4. Creatividad
        5. Bidding y presupuesto
        6. Optimization event
        
        Output: Score 47/100. Plan priorizado:
        - Crítico: CAPI sin firmar (event match 3.1). Resolver semana 1.
        - Crítico: 15 ad sets canibalizándose. Consolidar.
        - Importante: Creative fatigue en 8 campañas activas.
        - Oportunidad: ASC+ sin probar.
        
        Redistribución de presupuesto propuesta:
        - Adquisición core: -$30k → $24k
        - Retargeting: +$8k → $12k
        - ASC+ nuevo: $6k
```

### Flujo 3: Creative refresh por fatiga

```
Usuario: "Frequency de mis 3 anuncios principales pasó de 2 a 4.8 en 2 semanas.
        Necesito reemplazos urgentes."

Claude → /agencia:brief para reemplazo de creativos
        Captura:
        - Audiencia (la que está saturada)
        - Big idea actual (cuál se va)
        - Variantes a probar (3-5 conceptos distintos)
        - Mood board (referencias)
        - Plazo (urgente — 48h)
        
        + /agencia:copy meta-ads <nuevo concepto>
        Genera 3-5 variantes copy (primary text + headline + description)
        marcadas "safe" vs "experimental".
```

### Flujo 4: Respuesta crisis CM

```
Usuario: "Un cliente molesto publicó en FB diciendo que recibió producto dañado.
        Tiene 47 likes y comentarios negativos. ¿Cómo respondemos?"

Claude → (community-management-mx)
        Clasifica: queja con riesgo viral (>30 reacciones).
        
        Recomienda:
        1. Notificar al dueño/manager inmediatamente.
        2. Respuesta pública medida (no defensiva): empatía + commitment a resolver.
        3. Mover a DM en <2 horas con info de pedido específica.
        4. NO borrar el comentario.
        5. Después de resolver, follow-up al cliente para ver si actualiza opinión.
        
        Genera template de respuesta pública + DM inicial.
```

---

## Setup recomendado

### Estructura local

```
~/agencia-ops/
├── clientes/
│   ├── cinepolis/
│   │   ├── ficha.json
│   │   ├── manual-marca.md
│   │   └── targets-2026.json
├── reportes/
│   └── <cliente>/<año-mes>.md
├── auditorias/
├── briefs/
├── copy/
└── crisis/
    └── <fecha>-<cliente>.md
```

### Config

```json
{
  "agencia": {
    "razon_social": "...",
    "rfc": "...",
    "team": [
      {"nombre": "...", "rol": "AM", "email": "..."},
      {"nombre": "...", "rol": "Director Creativo", "email": "..."}
    ]
  },
  "preferencias": {
    "rounds_revision_default": 2,
    "buffer_creativo_dias": 3,
    "plataformas_default": ["meta", "google", "tiktok", "ga4"]
  }
}
```

---

## KPIs sugeridos

| KPI | Target | Razón |
|---|---|---|
| Tiempo en reporte por cliente | < 1h | El AM debe estar en estrategia, no copy-paste |
| Tiempo en cobranza al mes | < 4h total | Skill cobranza del core |
| % de creativos en fatiga detectados antes de afectar CPA | > 80% | Skill meta-ads-optimization |
| Templates aprobados en primer intento | > 70% | Validación pre-envío |
| Respuestas CM <30 min | > 90% en horario hábil | community-management-mx |

---

## Riesgos y limitaciones

- **Templates WhatsApp** no probados contra aprobación real Meta. Validar antes de subir a producción.
- **Tarifas Meta Ads citadas**: pueden estar desactualizadas (Meta cambia precios). Validar.
- **Reglas de Pixel/CAPI**: Meta actualiza requisitos regularmente.

---

## Ver también

- [estado-real.md](estado-real.md) — score honesto agencia-marketing-mx (4.6/9)
- [integracion-whatsapp.md](integracion-whatsapp.md) — para CM y avisos
