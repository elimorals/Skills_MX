# mp_repep_profeco

Registro Público para Evitar Publicidad (REPEP) — PROFECO (Arts. 18 y 18 BIS LFPC).

**Universo**: call centers + outbound telemarketing MX.

## Tools

- `repep_consultar(telefono)` — **handoff humano** (URL + pasos). `inscrito_repep: null`.
- `repep_filtrar_lote(telefonos[], lista_repep_path?)` — **real con la lista oficial**:
  filtra contra el archivo que el proveedor compra en PROFECO ("Comprar listas REPEP").
  Sin lista → handoff, nunca "todos contactables". Una lista sin números de 10 dígitos
  legibles → `ValidationError`.
- `repep_inscribir(telefono)` — handoff: la inscripción la hace el titular (web o 800 962 8000).
- `repep_estadisticas()` — sin cifras inventadas (PROFECO no publica el total de inscritos).

## Estado real

**Handoff humano** para la consulta individual. Revisado 2026-10-14 en
`https://repep.profeco.gob.mx/Solicitudnumero.jsp` (200, sin CAPTCHA visible) con un navegador
real y la línea institucional publicada por PROFECO (55 5568 8722 → ACTIVO): la consulta funciona
para una persona, pero el sitio tiene controles anti-automatización deliberados —redirección a
`audit.jsp`, nombre de campo aleatorio por sesión, beacon JS a `/c`, bloqueo de pegado y conteo de
movimientos de mouse/touch en `js/j_consulta.js`—. Con httpx el POST devuelve
"Ocurrió un error. Intenta de nuevo". Emularlos sería evadir un control anti-bot, así que no se hace
(misma regla que para CAPTCHAs). El canal para empresas es la lista oficial de pago.

Mock solo con `PLUGINS_MX_MOCK=1`. Antes el mock decidía "inscrito" por el último dígito del
número y `estadisticas` inventaba 22M inscritos y multas en UMAs.
