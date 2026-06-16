# mp_retys_catalogo

Catálogo Nacional de Regulaciones, Trámites y Servicios (**CONAMER**) normalizado a formato **DCAT** compatible con `datos.gob.mx` (Sistema Ajolote + CKAN).

**Universo**: 24 sectores oficiales, 12 trámites de alta demanda curados + expansión vivo CONAMER.

## Tools

- `retys_listar_sectores()` — 24 sectores con clave + nombre oficial
- `retys_buscar_tramite(q, sector?)` — búsqueda por texto + filtro sector
- `retys_detalle_tramite(homoclave)` — detalle por homoclave CONAMER (ej. SAT-04-022)
- `retys_exportar_dcat()` — exporta catálogo en JSON-LD DCAT para datos.gob.mx
- `retys_buscar_en_vivo(q)` — Playwright opt-in contra catalogonacional.gob.mx

## Producto comercial

- **Donación cívica** + contrato de mantenimiento con CONAMER/datos.gob.mx
- Diferenciador: exportador DCAT listo para ingest en Sistema Ajolote

## Path real

CONAMER usa **ASP.NET + AntiForgeryToken**. Selectores validados 2026-06-15:
- Search: `#txtSearch`
- Botón: `#btnSearch`
- Filtro dependencias: `#selectDependencias-selectized`

Activar con `MP_PLAYWRIGHT_PUBLIC=1` + `pip install playwright`.
