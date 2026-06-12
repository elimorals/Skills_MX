# mp_edomex_municipal — Portales Estado de México

⚠ Mock-first. EdoMex tiene portal único de tenencia pero predial por municipio (12+ portales distintos).

## Tools (4)

| Tool | Propósito |
|---|---|
| `edomex_consultar_predial` | Predial por municipio + cuenta |
| `edomex_consultar_tenencia` | Tenencia anual (EdoMex sí cobra) |
| `edomex_consultar_multas` | Multas tránsito |
| `edomex_listar_catalogos` | Municipios, tenencia, hoy no circula |

## Nota importante

EdoMex SÍ cobra tenencia anual (vs CDMX que subsidia). Verificar antes del 31 de marzo cada año.

## Tests

```bash
cd /Users/elias/Documents/Trabajo/skills/mcp-servers
.venv/bin/python -m pytest mp_edomex_municipal/tests/ -q
```
