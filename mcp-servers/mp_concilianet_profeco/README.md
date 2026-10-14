# mp_concilianet_profeco

Concilianet (conciliación en línea PROFECO) + Buró Comercial.

## Tools

- `concilianet_consultar_proveedor(razon_social)` — **real**: ¿aparece en los listados oficiales
  de proveedores en convenio? + coincidencias en el Buró Comercial.
- `concilianet_buro_quejas(proveedor, anio?)` — **real**: quejas recibidas/concluidas/conciliadas
  a nivel nacional por año y principales motivos.
- `concilianet_listar_proveedores()` — URLs de los dos PDF oficiales (no se devuelve una lista
  mal parseada: los PDF mezclan columnas de logos).
- `concilianet_estatus_caso(folio)` — handoff: el expediente solo lo ve el consumidor con su cuenta.
- `concilianet_registrar_queja(...)` — handoff con borrador; nunca registra (antes inventaba un folio).

## Estado real

Mock solo con `PLUGINS_MX_MOCK=1`. Fallas → `UpstreamError`. Requiere el extra
`publicos-federales-2` (pypdf) para leer los listados.

| Fecha | URL | Status | Resultado |
|---|---|---|---|
| 2026-10-14 | concilianet.profeco.gob.mx/Concilianet/proveedores_que_concilian.jsp | 200 | enlaza 2 PDF |
| 2026-10-14 | .../archivos/LISTADO DE PROVEEDORES PARTICIPANTES CONCILIANET.pdf | 200 | 968 KB (servicios) |
| 2026-10-14 | .../archivos/PROVEEDORES PARA PLATAFORMA CONCILIANET.pdf | 200 | 129 KB (telecom) |
| 2026-10-14 | burocomercial.profeco.gob.mx/proveedores (DataTables, search=volaris) | 200 | 4 de 57,158 proveedores |
| 2026-10-14 | burocomercial.profeco.gob.mx/consulta?type=anio\|edo\|quejas | 200 | Volaris 2019: 237 recibidas, 139 conciliadas |

Hallazgos: el catálogo mock de "32 proveedores en convenio" no coincide con el oficial (p. ej.
Volaris y Liverpool no aparecen en los PDF de 2026-10-14). `consulta?type=edo` responde JSON en
latin-1; se decodifica con respaldo. El Buró omite por ley las quejas en trámite y el nombre de
personas físicas.

Fixtures reales en `tests/fixtures/`. Live: `PLUGINS_MX_LIVE=1 pytest mp_concilianet_profeco -k live`.
