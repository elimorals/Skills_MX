# mp_cdmx_municipal — Portales CDMX

Predial, tenencia, multas y Hoy No Circula para Ciudad de México.

⚠ Path Playwright real NO implementado. Mock-first.

## Tools (5)

| Tool | Propósito |
|---|---|
| `cdmx_consultar_predial` | Status predial por cuenta |
| `cdmx_consultar_tenencia` | Status tenencia por placa (CDMX subsidia 100% < umbral) |
| `cdmx_consultar_multas` | Foto-infracciones + manuales por placa |
| `cdmx_consultar_hoy_no_circula` | Reglas del programa para una fecha |
| `cdmx_listar_catalogos` | Hologramas, status, tipos multa |

## Tests

```bash
cd /Users/elias/Documents/Trabajo/skills/mcp-servers
.venv/bin/python -m pytest mp_cdmx_municipal/tests/ -q
```
