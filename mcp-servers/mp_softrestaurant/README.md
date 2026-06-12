# mp_softrestaurant — MCP para Soft Restaurant POS

POS más usado en restaurantes MX. Local en SQL Server, **sin API REST**.

## Tools (8)

| Tool | Propósito |
|---|---|
| `softrest_corte_z` | Corte Z del día (totales por método/categoría) |
| `softrest_ventas_periodo` | Ventas detalladas en rango |
| `softrest_inventario_actual` | Inventario + alertas bajo stock |
| `softrest_platillos_vendidos` | Top 5/Bottom 5 — ingeniería menú |
| `softrest_meseros_ventas` | Ventas y propinas por mesero |
| `softrest_mesas_estatus` | Mesas libres/ocupadas/con orden (tiempo real) |
| `softrest_parsear_export` | Parser inline CSV |
| `softrest_listar_catalogos` | Categorías menú, métodos pago, status mesa |

## Configuración

| Variable | Propósito |
|---|---|
| `SOFT_RESTAURANT_EXPORTS_DIR` | Directorio con CSVs (corte_z_YYYYMMDD.csv, etc.) |
| `SOFT_RESTAURANT_DB_URL` | (Futuro) ODBC string al SQL Server local |

Mock-first sin variables.

## Configurar exports en Soft Restaurant

1. Abrir Soft Restaurant
2. Menú Reportes → Corte Z → Exportar a Excel
3. Guardar como `corte_z_YYYYMMDD.csv` en el directorio configurado
4. Repetir para ventas, platillos, meseros

Automatización recomendada: script Windows que exporta diariamente al cierre.

## Tests

```bash
.venv/bin/python -m pytest mp_softrestaurant/tests/ -q
```
