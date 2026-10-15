# mp_vivanuncios — MCP para vivanuncios.com.mx

⚠ Por ahora solo datos de ejemplo (`simulated: true`). Vivanuncios es multi-categoría (autos, inmuebles, empleos, electrónica, etc.).

## Tools (4)

| Tool | Propósito |
|---|---|
| `viv_buscar_anuncios` | Búsqueda con filtros por categoría + query + ciudad |
| `viv_obtener_detalle` | Detalle con datos del vendedor + métricas |
| `viv_publicar_anuncio` | Publicar nuevo anuncio (va a moderación) |
| `viv_listar_catalogos` | Categorías, tipos publicación, diferencias vs Inmuebles24 |

## Vivanuncios vs Inmuebles24

- **Vivanuncios**: mass-market multi-categoría, publicación más permisiva
- **Inmuebles24**: vertical inmuebles solamente, moderación más estricta, audiencia premium

## Tests

```bash
cd mcp-servers   # desde la raíz del clon
.venv/bin/python -m pytest mp_vivanuncios/tests/ -q
```
