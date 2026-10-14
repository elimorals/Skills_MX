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

- `lnetb_plazos_legales(fecha_referencia?)` — **real**: plazos de los artículos transitorios y si
  vencieron (los de días naturales con fecha; los de días hábiles sin fecha inventada).
- `lnetb_listar_indicadores()` — metodología propia de 10 indicadores (no es un indicador oficial).
- `lnetb_evaluar_estado`, `lnetb_ranking_nacional`, `lnetb_comparar_estados` — **solo con
  `PLUGINS_MX_MOCK=1`**; fuera de mock → `ConfigError`.

## Comprador objetivo

ATDT, IMCO, México Evalúa, prensa especializada.

## Estado real

Tipo: cálculo normativo local. Constantes verificadas contra el texto vigente
(https://www.diputados.gob.mx/LeyesBiblio/pdf/LNETB.pdf, "Nueva Ley DOF 16-07-2025", consultado
2026-10-14): entrada en vigor al día siguiente de la publicación (Transitorio Primero) → 17-jul-2025;
plazos de los transitorios Cuarto a Décimo Sexto. Cómputo: fecha de vigor + N días naturales
(Décimo Tercero/Cuarto vencen 2026-01-13; Décimo Quinto/Sexto, 2026-02-12).

Lo que se retiró del modo real:
- Los scores por estado (CDMX 85, BC 90, …): números curados a mano sin fuente trazable.
- La "meta 80 % de trámites digitales para 2030": no aparece en la Ley.

Pendiente para volver reales los scores: definir fuentes por indicador (p. ej. detección de
Llave MX en portales con `mp_llave_mx_tracker`, disponibilidad con `mp_portales_monitor`).
