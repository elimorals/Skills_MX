---
description: Genera reporte mensual ejecutivo de marketing digital para un cliente con KPIs por canal e insights accionables.
argument-hint: "<cliente> [mes-año]"
allowed-tools: Read, Write, Edit, Bash
---

# /agencia:reporte

Reporte mensual para: $ARGUMENTS

1. Invoca el skill `reporte-mensual-cliente`.
2. Lee datos del cliente en `clientes/[cliente]/` si existen (fichas, briefs previos, reportes anteriores).
3. Pide o lee:
   - CSVs/JSONs de cada canal activo (Meta Ads, Google Ads, TikTok, GA4, redes orgánicas)
   - Targets/KPIs del cliente (CPA, ROAS, conversiones, etc.)
   - Cualquier nota cualitativa del mes (campañas, eventos, cambios de producto)
4. Estructura el reporte siguiendo la plantilla del skill (resumen ejecutivo, KPIs globales, por canal, insights, top winners/losers, próximos pasos).
5. Genera versión completa en `reportes/[cliente]/YYYY-MM.md` y versión ejecutiva (1 página) en `reportes/[cliente]/YYYY-MM-resumen.md`.
6. Sugiere conversión a PDF o Google Slides para presentación.
7. Lista assets faltantes si algo no estuvo disponible.
