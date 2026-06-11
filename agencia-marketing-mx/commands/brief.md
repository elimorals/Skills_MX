---
description: Convierte una solicitud informal en brief creativo estructurado para diseño/copy/video/foto.
argument-hint: "<cliente> <proyecto>"
allowed-tools: Read, Write, Edit
---

# /agencia:brief

Brief creativo para: $ARGUMENTS

1. Invoca el skill `briefing-creativo`.
2. Recopila estructuradamente:
   - Contexto del cliente y producto/servicio
   - Objetivo principal de negocio (forzar a UN solo objetivo)
   - KPIs específicos con target y plazo
   - Audiencia objetivo con insight (no solo demografía)
   - Mensaje clave y big idea
   - Tono y referencias de tono
   - Entregables exhaustivos con formato y cantidad
   - Mood board y referencias visuales
   - Workflow con fechas
3. Genera brief completo en `briefs/[cliente]/YYYY-MM-DD-[proyecto].md`.
4. Genera versión executive summary 1 página.
5. Lista preguntas pendientes si faltan datos críticos (típicamente: audiencia con insight, referencias visuales, presupuesto).
6. Sugiere flujo de aprobación con cliente antes de pasar a ejecución.
