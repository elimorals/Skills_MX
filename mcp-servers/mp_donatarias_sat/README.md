# mp_donatarias_sat

Padrón de donatarias autorizadas del SAT (Art. 79/82 LISR, Anexo 14 RMF).

## Tools

- `donatarias_consultar(rfc)` — ¿está autorizada para emitir recibos deducibles?
- `donatarias_buscar(razon_social, [entidad], [limite])`
- `donatarias_listar_por_entidad(entidad)` — máx. 200 en la respuesta (`total` trae el conteo real).
- `donatarias_estadisticas()` — total y conteos por entidad y rubro.
- `donatarias_listar_rubros()` — catálogo local (letras A–M del directorio).

## Estado real (2026-10-14)

**Real** por default (fuente pública). Mock solo con `PLUGINS_MX_MOCK=1`. Si la
fuente falla → `UpstreamError`, sin fallback a mock.

Fuente: [Directorio de Donatarias Autorizadas](https://www.sat.gob.mx/minisitio/DonatariasAutorizadas/padron_directorio.html).
El cliente lee esa página, toma el primer `Dir_<año>.xlsx` enlazado y lo parsea
con la stdlib (zipfile + xml, sin openpyxl). Directorio en cache 7 días.

| Validación en vivo | Resultado |
|---|---|
| 2026-10-14 `GET .../padron_directorio.html` | 200 (las rutas viejas `sat.gob.mx/consultas/27717/...` dan 403) |
| 2026-10-14 `GET .../documentos/padron_donatarias/Dir_2026.xlsx` | 200, 5.7 MB, `last-modified` 2026-10-06; 15,375 filas → 10,017 RFC únicos; encabezado: "Anexo 14 RMF, DOF 09-ene-2026" |
| `donatarias_consultar("AAC101117RP1")` | autorizada, AGS, actividades A + M |

Limitaciones:

- El directorio no incluye revocaciones posteriores a su corte: la página del
  SAT publica aparte PDFs de revocadas y "pendientes de publicar en DOF" (no se
  parsean). Una respuesta `autorizada: false` lo advierte.
- Columnas de contacto y objeto social del XLSX no se exponen.
