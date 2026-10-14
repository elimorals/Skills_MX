# mp_dof_api

Diario Oficial de la Federación: sumario del día, búsqueda en títulos,
texto completo de notas y monitoreo por palabra clave.

## Tools

| Tool | Para qué |
|---|---|
| `dof_sumario_dia(fecha)` | Notas publicadas un día (matutina, vespertina, extraordinaria) |
| `dof_buscar_texto(texto, desde, hasta, limite)` | Busca en **títulos**; rango máx 31 días (default últimos 30) |
| `dof_detalle_nota(codigo, fecha)` | Texto completo (HTML → texto) + metadatos |
| `dof_monitorear_por_keyword(keywords, dias_atras)` | Varias palabras, hasta 30 días atrás |
| `dof_listar_dependencias_comunes()` | Catálogo local |

## Estado real

| Fecha | URL | Resultado |
|---|---|---|
| 2026-10-14 | `GET https://sidof.segob.gob.mx/dof/sidof/notas/13-10-2026` | 200 JSON, 175 notas matutinas |
| 2026-10-14 | `GET https://sidof.segob.gob.mx/dof/sidof/notas/nota/5800977` | 200 JSON, `cadenaContenido` HTML del decreto |

- Estado: **real validado** (test `@pytest.mark.live` en `tests/test_real.py`).
- Fuente: API JSON pública de SIDOF (Segob), la que usa el portal. Sin login ni CAPTCHA.
- SIDOF no expone búsqueda full-text: `buscar_texto` recorre los sumarios diarios
  del rango (1 petición por día) y filtra por título, sin acentos ni mayúsculas.
  Algunas notas no traen `titulo` en el sumario y no aparecen en la búsqueda.
- Errores → `UpstreamError`; nota inexistente → `NotFoundError`. Sin fallback a mock.
- Mock solo con `PLUGINS_MX_MOCK=1` (`simulated: true`).

Test live: `PLUGINS_MX_LIVE=1 .venv/bin/pytest mp_dof_api -k live`.
