---
description: Audita una cuenta completa de Meta Ads (Pixel/CAPI, estructura, audiencias, creativos, bidding) y entrega plan priorizado de optimización.
argument-hint: "<cliente>"
allowed-tools: Read, Write, Edit, Bash
---

# /agencia:auditoria-cuenta

Auditoría Meta Ads para: $ARGUMENTS

1. Invoca el skill `meta-ads-optimization`.
2. Pide o lee:
   - Acceso a la cuenta (mejor) o export CSV últimos 30+ días
   - Pixel/CAPI setup
   - Goals del cliente (CPA target, ROAS target, KPI principal)
3. Ejecuta checklist de 6 áreas: tracking, estructura, audiencias, creatividad, bidding, eventos.
4. Genera reporte de auditoría con:
   - Score global /100
   - Hallazgos críticos (resolver antes de cualquier optimización)
   - Hallazgos importantes (resolver en 7 días)
   - Oportunidades (mejora gradual)
   - Plan de acción priorizado por semana
   - KPIs de seguimiento
5. Guarda en `auditorias/[cliente]/YYYY-MM-DD-meta-ads.md`.
6. Si hay redistribución de presupuesto recomendada, incluir tabla específica con proyección.
