# ADR 008 — Estado real por MCP, sin fallback silencioso a datos de ejemplo

**Status**: ACEPTADO  (2026-10-14) · Reemplaza a [ADR 002](002-mcps-mock-first.md)

## Context

El ADR 002 dejó todos los MCPs en modo mock por defecto. Sirvió para arrancar sin credenciales, pero en junio de 2026 ya causaba tres problemas:

- **Fallback silencioso.** Varios clientes, si el portal fallaba o la credencial era inválida, caían a datos simulados. Con credenciales configuradas, el usuario podía recibir una respuesta inventada sin enterarse.
- **"Producción" sin evidencia.** Los README y `STATUS.md` declaraban MCPs "en producción (mock + real)" sin que nadie hubiera hecho una sola llamada real. Las cifras de esos documentos ya no corresponden al código.
- **Portales con CAPTCHA o login.** Cada MCP resolvía la imposibilidad de consultar a su manera (stub, mock o error genérico).

## Decision

La oleada 1 (plan en [`docs/plan-mock-a-real.md`](../plan-mock-a-real.md)) fija estas reglas para los 83 MCPs:

1. **Sin fallback silencioso.** Con credenciales configuradas, cualquier error del proveedor se propaga como error tipado (`AuthError`, `UpstreamError`, `NotFoundError`, `ConfigError`…). Nunca se sustituye por datos de ejemplo.
2. **Datos de ejemplo solo explícitos.** Sin credenciales, el MCP responde datos de ejemplo marcados `simulated: true`. `PLUGINS_MX_MOCK=1` fuerza ese modo. `shared/mock.py` sigue siendo el único punto que decide.
3. **Estado real por MCP.** Cada `mp_*/README.md` tiene una sección "## Estado real" con lo que se validó en vivo, cuándo y contra qué URL. `scripts/generar-estado-mcps.py` arma con esas secciones `mcp-servers/CATALOGO.md`, la tabla del README raíz y el sitio. Las categorías son: real validado en vivo, real sin validar (falta credencial), entrega a humano, sin API pública, cálculo normativo verificado, bloqueado y sin verificar.
4. **Validación en vivo para llamarlo "real".** Al menos una llamada exitosa documentada y un test `@pytest.mark.live` (corre con `PLUGINS_MX_LIVE=1`).
5. **CAPTCHA y login: entrega a humano unificada.** `shared/portal_handoff.py` devuelve URL, pasos y campos prellenados con un formato único. El solver de CAPTCHA (`shared/captcha_solver.py`) es opt-in con `PLUGINS_MX_CAPTCHA_SOLVER=2captcha` + `TWOCAPTCHA_API_KEY`. No evade anti-bots de red, y `citas_monitor` y REPEP quedan excluidos por diseño.
6. **Sin API pública: error explícito.** Si el proveedor no publica API, con credenciales el tool devuelve `ConfigError` con `motivo: sin_api_publica` y la alternativa manual.
7. **Solo lectura en vivo.** Las pruebas reales no presentan declaraciones, no agendan citas, no modifican obligaciones ni mueven dinero.

## Alternatives considered

1. **Mantener mock-first y solo documentar.** Descartado: el riesgo real es la respuesta inventada con credenciales activas, y documentar no lo evita.
2. **Real por defecto, sin datos de ejemplo.** Descartado: los demos, el CI y los contribuidores sin credenciales necesitan respuestas. Basta con que vayan marcadas `simulated: true`.
3. **Tabla de estado mantenida a mano.** Descartado: es justo lo que se desfasó en junio. El estado se genera desde los README y el CI lo verifica con `--check`.

## Consequences

**Positivas**:
- Una respuesta sin `simulated: true` viene del proveedor real o es un error. No hay un tercer caso.
- El estado publicado (README, CATALOGO, sitio) sale de una sola fuente, y el CI detecta cuando se desfasa.
- Los portales con CAPTCHA o login se comportan igual para la skill que los consume.

**Negativas**:
- Sin credenciales, una consulta que antes "funcionaba" con mock ahora devuelve `simulated: true`, o un handoff que pide intervención humana.
- 13 MCPs quedan "real sin validar" hasta tener credenciales, y el grupo de login de usuario final (IMSS, INFONAVIT, bancos, Buró, CFE, Telmex) sigue pendiente de capturas HAR (oleada 2).

## Ver también

- [ADR 002](002-mcps-mock-first.md) (reemplazada)
- `mcp-servers/shared/mock.py`, `mcp-servers/shared/portal_handoff.py`, `mcp-servers/shared/captcha_solver.py`, `mcp-servers/shared/errors.py`
- [`mcp-servers/CATALOGO.md`](../../mcp-servers/CATALOGO.md)
