# mp_lnetb_auditor

Auditor LNETB (**Ley Nacional Eliminar Trámites Burocráticos** — DOF 16-jul-2025).

México Evalúa documentó que el gobierno **NO publica ranking nominal** del avance estatal. Este MCP lo construye con metodología explícita.

## Indicadores (10 ponderados, suma 100)

| Clave | Indicador | Peso |
|---|---|---|
| i1_portal_unificado | Portal único trámites estatal | 15 |
| i2_sso_ciudadano | SSO ciudadano | 10 |
| i3_pagos_digitales | Pagos digitales | 15 |
| i4_firma_electronica | Firma electrónica estatal | 10 |
| i5_simplificacion_total | Trámites simplificados / total | 15 |
| i6_atencion_chatbot | Canal IA / chatbot ciudadano | 5 |
| i7_transparencia | Transparencia datos abiertos | 10 |
| i8_apps_oficiales | Apps móviles oficiales | 5 |
| i9_interoperabilidad | Interoperabilidad fed-estatal | 10 |
| i10_conectividad | Conectividad (MX Conectado) | 5 |

## Tools

- `lnetb_listar_indicadores()` — 10 indicadores con peso
- `lnetb_evaluar_estado(estado_clave)` — score 0-100 + brecha vs meta 80%
- `lnetb_ranking_nacional(top)` — top N estados
- `lnetb_comparar_estados(estados)` — comparativa 2-10 estados

## Comprador objetivo

ATDT, IMCO, México Evalúa, prensa especializada (Animal Político, Expansión Política).

## Meta LNETB 2030

80% trámites digitales nacionales (sin estados rezagados publicados oficialmente).
