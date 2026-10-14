# mp_cnbv_fintech

Instituciones de Tecnología Financiera (Ley Fintech): IFPE y IFC en el
Padrón de Entidades Supervisadas (PES) de la CNBV.

## Tools

| Tool | Para qué |
|---|---|
| `cnbv_fintech_consultar_itf(nombre, rfc)` | ¿Es IFPE/IFC supervisada? En real busca por `nombre` |
| `cnbv_fintech_listar_ifpe()` | IFPE en el PES (en vivo) |
| `cnbv_fintech_listar_ifc()` | IFC (crowdfunding) en el PES (en vivo) |
| `cnbv_fintech_listar_modelos_novedosos()` | Solo mock: no hay fuente pública estructurada |
| `cnbv_fintech_verificar_contraparte(nombre, tipo_operacion)` | Compliance Art. 5 Ley Fintech |

## Estado real

| Fecha | URL | Resultado |
|---|---|---|
| 2026-10-14 | `GET https://pes.cnbv.gob.mx/Consulta/ConsultaEntidad?subsectorName=INSTITUCIONES DE FONDOS DE PAGO ELECTRÓNICO` | 200 HTML, 51 IFPE |
| 2026-10-14 | `GET .../ConsultaEntidad?entidad=MERCADOLIBRE` | 200 HTML, 1 fila IFPE (CASFIM 65-…) |
| 2026-10-14 | `https://www.cnbv.gob.mx/Paginas/PADRON-DE-ENTIDADES-SUPERVISADAS.aspx` (URL anterior del MCP) | 404 sin acento; la página vigente enlaza a `pes.cnbv.gob.mx` |

- Estado: **real validado** para `listar_ifpe`, `listar_ifc`, `consultar_itf(nombre)` y
  `verificar_contraparte(nombre)` (test `@pytest.mark.live`).
- El PES **no publica RFC**: en modo real `consultar_itf` con solo `rfc` → `ValidationError`.
- Estar en el PES = entidad supervisada; el MCP devuelve `estado: "Supervisada (PES)"`.
- `listar_modelos_novedosos` en real → error `sin_fuente_publica` (no hay padrón
  estructurado; buscar en DOF con `mp_dof_api`).
- Errores → `UpstreamError`; sin fallback. Mock (snapshot ilustrativo con RFCs
  ficticios) solo con `PLUGINS_MX_MOCK=1`.

Test live: `PLUGINS_MX_LIVE=1 .venv/bin/pytest mp_cnbv_fintech -k live`.
