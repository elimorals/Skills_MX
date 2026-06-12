# restaurante-mx

Plugin para restaurantes, dark kitchens, cafeterías y bares en México.

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
