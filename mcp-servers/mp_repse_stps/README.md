# mp_repse_stps

MCP standalone para consulta REPSE STPS (Registro Público de empresas de Subcontratación).

**Portal**: https://repse.stps.gob.mx/ — consulta pública sin CAPTCHA ni login; el MCP llama con `httpx` a los endpoints JSON del formulario "Consultar Padrón".

## Por qué importa

- Reforma laboral 2021 (Art. 15 LFT) obligó a TODO proveedor de servicios especializados a registrarse en REPSE.
- Si contratas a un proveedor SIN REPSE vigente, **te vuelves responsable solidario laboral y fiscal** de sus trabajadores. Esto incluye salarios caídos, finiquitos, IMSS, INFONAVIT y créditos fiscales.
- Universo afectado: **TODA empresa B2B mexicana** que terceriza nómina, IT, limpieza, seguridad, contabilidad, marketing, etc.

## Tools expuestas

| Tool | Para qué |
|------|----------|
| `repse_consultar_por_razon_social` | Búsqueda fuzzy por nombre o razón social |
| `repse_consultar_por_numero_registro` | Detalle completo de registro (vigencia, servicios) |
| `repse_verificar_proveedor` | Compliance B2B: ¿puedo contratar a este proveedor? |

## Flujo `repse_verificar_proveedor` (compliance Art. 15 LFT)

```
input: razon_social="MANPOWER CORPORATIVO"
   │
   ├─→ ¿Aparece en REPSE?
   │    NO → puede_contratar=False, advertencia "responsable solidario"
   │    SÍ → continuar
   │
   ├─→ ¿Vigencia >= hoy?
   │    NO → puede_contratar=False, advertencia "debe renovar"
   │    SÍ → puede_contratar=True
   │
   └─→ Return detalle + decision
```

## Tipos de datos REPSE

- **Número de registro / folio REPSE**: el folio que muestra el portal (ej. `2775`).
  La búsqueda acepta folio, RFC o razón social.
- **Aviso de registro**: `<abreviatura>-<num_emi>/<año>` (ej. `ARRMGST-6/2024`)
- **id_padron**: id interno que devuelve la búsqueda (no es el folio)
- **Vigencia**: 3 años desde la fecha de aviso de registro

## Estado real

| Fecha | URL | Resultado |
|---|---|---|
| 2026-10-14 | `GET https://repse.stps.gob.mx/busca_razon_social?term=BIMBO` | 200 JSON, 2 coincidencias |
| 2026-10-14 | `POST https://repse.stps.gob.mx/buscar-padron` (id 2235) | 200 JSON, folio 2775, vigencia 2027-05-09 |
| 2026-10-14 | `POST .../buscar-padron` (id inexistente) | 200 JSON `registro: 0` → `NotFoundError` |

- Estado: **real validado** (test `@pytest.mark.live` en `tests/test_real.py`).
- Flujo: `GET /` (cookie + meta `csrf-token`) → `GET /busca_razon_social?term=` →
  `POST /buscar-padron` (multipart `razon_social=<id>`, header `X-CSRF-TOKEN`).
- Errores del portal → `UpstreamError`; sin fallback a mock.
- Mock solo con `PLUGINS_MX_MOCK=1` (`simulated: true`).
- `/app/` (la SPA anterior) devuelve 404 desde 2026.

Test live: `PLUGINS_MX_LIVE=1 .venv/bin/pytest mp_repse_stps -m live`.

## Cache

30 días por consulta. El padrón cambia raramente (altas/bajas/renovaciones).

## Tests

```bash
PYTHONPATH=mcp-servers pytest mcp-servers/mp_repse_stps/tests/ -v
```
