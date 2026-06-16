# mp_llave_mx_tracker

Tracker público de adopción **Llave MX** por dependencia federal y estatal.

**Universo**: 20 dependencias monitoreadas (15 federales + 5 estatales).
**Producto**: para ATDT (José Merino), IMCO, México Evalúa, prensa especializada.

## Tools

- `llave_mx_listar_dependencias(nivel?)` — lista filtrable por federal/federal_autonomo/estatal
- `llave_mx_estatus_dependencia(clave)` — detalle por clave (sat, imss, ine, cdmx, etc.)
- `llave_mx_estadisticas_nacionales()` — % integrado vs meta LNETB 2030 (80%)
- `llave_mx_verificar_en_vivo(clave)` — Playwright opt-in (heurística OAuth)

## Path real

Setear `MP_PLAYWRIGHT_PUBLIC=1` y `pip install playwright` para verificación en vivo.
La heurística busca:
1. Texto "Llave MX" o "Iniciar sesión con Llave" en el HTML
2. Enlaces a `llave.gob.mx/oauthV2.xhtml`
3. Redirección al portal OAuth

## Fuente legal

- Lineamientos Llave MX (SIDOF 2025)
- Ley Nacional Eliminar Trámites Burocráticos (DOF 16-jul-2025) — meta 80% para 2030
