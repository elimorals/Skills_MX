# mp_simplifica_ciudadano

Tracker Ley Nacional para Eliminar Trámites Burocráticos (DOF 16-jul-2025).

**Universo**: ciudadanos + empresas afectados por trámites locales en 32 estados.

## Tools

- `simplifica_estado(estado_clave)` — avance %, trámites simplificados, destacados.
- `simplifica_tracker_nacional()` — promedio nacional + top 3 + rezagados.
- `simplifica_comparar_estados(estados_claves[])` — ranking por avance.

## Estado real

**Bloqueado: no hay fuente pública.** Revisado 2026-10-14: ni la ATDT ni datos.gob.mx
(`package_search?q=simplificacion` → 0 datasets) publican avance de simplificación por estado.
Las cifras del catálogo eran un "mock representativo"; ahora solo se sirven con
`PLUGINS_MX_MOCK=1` (marcadas `simulated: true`). Fuera de mock las tres tools devuelven
`ConfigError` explicando que el dato no existe públicamente.

Corregido: la URL de la ley apuntaba a un código DOF inventado; ahora apunta al texto vigente
(https://www.diputados.gob.mx/LeyesBiblio/pdf/LNETB.pdf). Publicación DOF 16-07-2025, vigor 17-07-2025.
Para plazos legales reales de la LNETB usar `mp_lnetb_auditor` (`lnetb_plazos_legales`).
