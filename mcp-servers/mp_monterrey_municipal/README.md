# mp_monterrey_municipal — AMM (Área Metropolitana de Monterrey)

⚠ Mock-first. Cubre los 9 municipios del AMM Nuevo León.

## Tools (4)

| Tool | Propósito |
|---|---|
| `nl_consultar_predial` | Predial por municipio del AMM |
| `nl_consultar_multas` | Multas de tránsito NL |
| `nl_consultar_calidad_aire` | IMECA + contingencia Aire Limpio |
| `nl_listar_catalogos` | Municipios AMM, contingencias |

## Tests

```bash
cd /Users/elias/Documents/Trabajo/skills/mcp-servers
.venv/bin/python -m pytest mp_monterrey_municipal/tests/ -q
```
