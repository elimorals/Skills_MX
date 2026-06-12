---
name: workflow-respuesta-crisis-cm
description: Workflow de respuesta a crisis para community management (CM). Cuando se detecta una crítica viral o crisis en redes sociales del cliente, orquesta: análisis sentimiento, identificación influencers participantes, draft de respuestas por canal (Twitter/X, Facebook, Instagram, TikTok), aprobación cliente, ejecución coordinada. Usar cuando el usuario diga crisis cm, viral negativo, respuesta crisis redes, queja viral cliente.
allowed-tools: Read, Write
---

# Workflow respuesta a crisis CM

## Trigger

- Detección de tweet/post viral negativo
- Aumento súbito menciones negativas (> 3x baseline)
- Influencer con > 100k seguidores criticando

## Fases

### 1. Análisis (15-30 min)
- Sentimiento del trending (neg/neutral/pos %)
- Alcance estimado (cuentas + impresiones)
- Hashtags relacionados
- Influencers participantes principales

### 2. Clasificar severidad

| Nivel | Criterio | Acción |
|---|---|---|
| 🟢 Bajo | < 100 menciones | Monitoreo, no respuesta proactiva |
| 🟡 Medio | 100-1,000 menciones | Respuesta corporativa estándar |
| 🟠 Alto | 1,000-10,000 | Disculpa formal + correctivos publicados |
| 🔴 Crítico | > 10,000 + medios | C-suite involucrado + PR consultora |

### 3. Draft de respuesta

Por canal:
- Twitter/X: < 280 caracteres, tono empático
- Facebook: detallado, link a comunicado
- Instagram: imagen + caption corto
- TikTok: video respuesta (no escrito)

### 4. Aprobación

⚠ NO publicar sin firma de cliente C-suite o director marketing.

### 5. Publicación coordinada

Todas las redes a la misma hora (10-30 min apart máximo).

### 6. Post-crisis tracking

- Sentimiento 24h después
- Sentimiento 7 días después
- Lecciones aprendidas para playbook
