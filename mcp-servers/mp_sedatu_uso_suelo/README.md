# mp_sedatu_uso_suelo

Licencias municipales + RETyS (Registro Estatal de Trámites y Servicios).

## Tools

- `sedatu_buscar_tramite(estado, municipio, clave_tramite)` — duración + requisitos.
- `sedatu_consultar_uso_suelo(estado, municipio, giro_propuesto)` — usos compatibles.
- `sedatu_estimar_construccion(estado, municipio, m2, uso?)` — derechos + estudios requeridos.
- `sedatu_listar_tramites()` — 6 trámites catalogados.

## Estado real

**Handoff humano / orientativo.** El uso de suelo lo fija cada municipio en su PDU; no hay
consulta pública nacional de zonificación por predio (revisado 2026-10-14). Fuera de
`PLUGINS_MX_MOCK=1`:

- `consultar_uso_suelo_permitido` → `permitido: null` + pasos (antes devolvía `True` siempre).
- `buscar_tramite` → requisitos genéricos con `verificado: false`, sin costos ni plazos inventados.
- `estimar_construccion` → `ConfigError` (los derechos por m² los fija cada ley de ingresos municipal).

Para CDMX y municipios con portal propio ver los MCPs municipales (grupo E).
