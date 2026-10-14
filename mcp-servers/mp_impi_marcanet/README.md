# mp_impi_marcanet

Búsqueda de marcas en el IMPI vía **MARCia** (https://marcia.impi.gob.mx/).
El nombre `marcanet` se conserva por compatibilidad; MARCANET ya no existe.

## Por qué importa

- **Universo**: legaltech, agencias creativas, startups, marketplaces.
- **Caso de uso**: validar si una denominación ya está registrada antes de pagar
  un trámite IMPI.

## Tools

### `impi_buscar(query, limite=20, incluir_raw=False)`
Búsqueda rápida (denominación, titular o número). Devuelve total y los primeros
`limite` resultados.

### `impi_verificar_denominacion(denominacion)`
Cuenta coincidencias exactas/similares en la primera página. No sustituye el
análisis de similitud fonética/gráfica que hace el IMPI.

## Estado real

| Fecha | URL | Resultado |
|---|---|---|
| 2026-10-14 | `GET https://marcia.impi.gob.mx/marcas/search/quick` | 200, cookies `JSESSIONID`, `SESSIONTOKEN`, `XSRF-TOKEN` |
| 2026-10-14 | `POST .../marcas/search/internal/record` (`TELMEX`) | 200 JSON, `count` 5305 |
| 2026-10-14 | `POST .../marcas/search/internal/result` | 200 JSON, `resultPage` con registro 340988 |
| 2026-10-14 | `https://vidoc.impi.gob.mx` (fuente anterior) | exige token reCAPTCHA v3: descartada |

- Estado: **real validado** (test `@pytest.mark.live` en `tests/test_marcia.py`).
- Sin CAPTCHA ni login; el único requisito es reenviar la cookie `XSRF-TOKEN`
  como header `X-XSRF-TOKEN`.
- Errores → `UpstreamError`; sin fallback a mock.
- Mock solo con `PLUGINS_MX_MOCK=1` (`simulated: true`).

## Schema de respuesta (real)

```json
{
  "query": "TELMEX",
  "total_encontrados": 5305,
  "devueltos": 5,
  "resultados": [
    {
      "expediente": "RM198600012166",
      "numero_expediente": "12166",
      "numero_registro": "340988",
      "area": "MARCAS",
      "tipo_expediente": "REGISTRO DE MARCA",
      "denominacion": "TELMEX",
      "estatus": "REGISTRADO",
      "titular": "MARTEX POTOSI, S.A. DE C.V.",
      "titulares": ["MARTEX POTOSI, S.A. DE C.V."],
      "clases_niza": [],
      "fecha_solicitud": "24/7/1986",
      "fecha_vigencia": "24/07/2031",
      "imagen_url": "https://marcia.impi.gob.mx/marcas/image/RM198600012166"
    }
  ],
  "fuente": "https://marcia.impi.gob.mx/marcas/search/quick",
  "modo": "marcia",
  "simulated": false
}
```

## Tests

```bash
.venv/bin/pytest mp_impi_marcanet
PLUGINS_MX_LIVE=1 .venv/bin/pytest mp_impi_marcanet -k live
```
