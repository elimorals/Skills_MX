# mp_inmuebles24 — MCP para inmuebles24.com

⚠ Mock-first. Búsqueda y detalle pueden hacerse vía HTTP simple, publicación requiere Playwright + cuenta vendedor.

## Tools (5)

| Tool | Auth | Mock |
|---|---|---|
| `inm24_buscar_inmuebles` | Pública | Sí |
| `inm24_obtener_detalle` | Pública | Sí |
| `inm24_buscar_comparables_zona` | Pública | Sí |
| `inm24_publicar_listing` | Cuenta vendedor | Sí |
| `inm24_listar_catalogos` | — | Local |

## Casos de uso

- **Análisis comparativo zona**: para definir precio de renta o venta
- **Búsqueda agente inmobiliario**: cribar listings para clientes
- **Publicación batch**: crear listings desde catálogo propio
- **Monitoreo competencia**: ver listings similares para ajustar pricing

## Tests

```bash
cd /Users/elias/Documents/Trabajo/skills/mcp-servers
.venv/bin/python -m pytest mp_inmuebles24/tests/ -q
```
