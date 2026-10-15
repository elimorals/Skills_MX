# restaurante-mx

Plugin para restaurantes, dark kitchens, cafeterías y bares en México.

## Instalación

```bash
/plugin marketplace add elimorals/Skills_MX
/plugin install core-mexico --marketplace elimorals/Skills_MX   # base de todos los verticales
/plugin install restaurante-mx --marketplace elimorals/Skills_MX
```

Los MCPs del plugin se descargan solos con [`uv`](https://docs.astral.sh/uv/) la primera vez. Sin credenciales responden datos de ejemplo marcados `simulated: true`; con credenciales, los errores del proveedor se propagan. Estado por MCP: [`mcp-servers/CATALOGO.md`](../mcp-servers/CATALOGO.md).

## Casos de uso

- **Restaurante tradicional** (mesas + cocina propia): ingeniería menú + propinas + delivery
- **Dark kitchen**: 100% delivery via aggregators
- **Cafetería de especialidad**: control mermas (café, leche)
- **Food truck / móvil**: simplificado, sin propinas
- **Bar / cantina**: alto margen bebidas, control inventario alcohol

## Skills propios (5)

| Skill | Cuándo activa |
|---|---|
| `menu-ingenieria-margen` | Matriz BCG (estrellas, vacas, perros, dilemas) por plato |
| `inventario-merma` | Costos + merma proyectada + alertas reposición |
| `propinas-distribucion` | Distribución a meseros, cocina, bar |
| `delivery-aggregators` | Rappi (32%) + DiDi (25%) + UberEats (30%) — comisiones distintas |
| `cfdi-publico-global` | CFDI mensual consolidado para ventas B2C sin RFC |

## Comandos

```
/restaurante:ingenieria-menu
/restaurante:cierre-caja
/restaurante:sync-aggregators
/restaurante:distribuir-propinas
```

## Estado

⚠ Scaffolding (v0.1.0). Validar comisiones aggregators 2026 contra contratos reales.
