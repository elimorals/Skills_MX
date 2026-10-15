---
name: menu-ingenieria-margen
description: Ingeniería de menú para restaurantes mexicanos usando matriz BCG (estrellas, vacas, perros, dilemas) basada en popularidad (ventas) y margen (precio - food cost). Identifica platos a promover, reposicionar, rediseñar o eliminar. Calcula food cost objetivo (25-35%), precio sugerido para alcanzar margen objetivo, alternativas para reducir costo de ingredientes. Usar cuando el usuario diga ingeniería menú, qué platos quitar, plato más rentable, food cost, margen restaurante, optimizar menú. NO usar para inventario (otro skill) ni delivery aggregators.
allowed-tools: Read, Write, Edit
---

# Ingeniería de menú

Cada plato en el menú compite por espacio en la cocina, en el menú impreso y en la mente del cliente.

## Matriz BCG aplicada a menú

| Categoría | Popularidad | Margen | Acción |
|---|---|---|---|
| **Estrella ⭐** | Alta | Alto | Promover + destacar en menú |
| **Vaca lechera 🐄** | Alta | Bajo | Subir precio o reducir food cost |
| **Dilema ❓** | Baja | Alto | Reposicionar, mejorar fotos/descripción |
| **Perro 🐶** | Baja | Bajo | Eliminar o rediseñar completamente |

## Cómo calcular cada plato

### 1. Food Cost (costo del ingrediente)

```
food_cost_porcentaje = costo_ingredientes / precio_venta
```

Rangos de referencia de la industria (sin fuente oficial; varían por tipo de cocina):
- **Excelente**: 25-30%
- **Bueno**: 30-35%
- **Aceptable**: 35-38%
- **Malo**: > 38% (refactorizar)

### 2. Contribución por plato

```
margen_unitario = precio_venta - food_cost
contribucion_total = margen_unitario × unidades_vendidas
```

### 3. Popularidad

```
popularidad_porcentaje = unidades_vendidas / total_platos_vendidos
```

Umbral de "popular" (método Kasavana-Smith): `popularidad ≥ 70% × (1 / número_de_platos)`.

### 4. Margen alto vs bajo

```
margen_promedio_ponderado = sum(contribucion_total) / sum(unidades_vendidas)
margen alto  ⇔ margen_unitario ≥ margen_promedio_ponderado
```

La clasificación usa el **margen en pesos**, no el food cost %. El food cost % se revisa aparte como alerta (un plato puede tener margen alto en pesos y FC% malo).

## Ejemplo: 5 platos de un menú

| Plato | Precio | Food Cost | FC % | Vendidos/mes | Margen/u | Total mes |
|---|---|---|---|---|---|---|
| Mole poblano | $280 | $85 | 30% | 320 | $195 | $62,400 |
| Tacos al pastor | $145 | $35 | 24% | 850 | $110 | $93,500 |
| Pozole | $195 | $75 | 38% | 90 | $120 | $10,800 |
| Aguachile | $310 | $145 | 47% | 65 | $165 | $10,725 |
| Ensalada César | $165 | $42 | 25% | 180 | $123 | $22,140 |

### Análisis BCG

Umbrales del ejemplo:
- Unidades totales: 320 + 850 + 90 + 65 + 180 = 1,505 → umbral de popularidad = 70% × 1,505 / 5 = **210.7 unidades**
- Contribución total: 62,400 + 93,500 + 10,800 + 10,725 + 22,140 = $199,565 → margen promedio ponderado = 199,565 / 1,505 = **$132.60**

| Plato | Popular (≥ 210.7) | Margen alto (≥ $132.60) | Categoría |
|---|---|---|---|
| Mole poblano | Sí (320) | Sí ($195) | ⭐ Estrella |
| Tacos al pastor | Sí (850) | No ($110) | 🐄 Vaca |
| Aguachile | No (65) | Sí ($165) | ❓ Dilema |
| Pozole | No (90) | No ($120) | 🐶 Perro |
| Ensalada César | No (180) | No ($123) | 🐶 Perro |

- **Mole poblano** ⭐: mantener receta y precio, darle la mejor posición en la carta
- **Tacos al pastor** 🐄: el plato que más vende pero deja menos por unidad → subir precio poco a poco (p. ej. +$10) o bajar costo de porción sin tocar calidad percibida
- **Aguachile** ❓: deja buen margen en pesos pero vende poco → reposicionar (foto, descripción, sugerencia del mesero). Ojo: FC 47% → revisar costo de ingredientes
- **Pozole** 🐶 y **Ensalada César** 🐶: rediseñar (receta, precio, presentación) o retirar; César tiene buen FC% (25%) pero bajo margen en pesos y poca venta

## Cómo reducir food cost

### Opciones por orden de impacto

1. **Renegociar proveedor**: -5-15% en items principales
2. **Sustituir ingrediente caro por uno similar**:
   - Atún → atún en lata (si receta lo permite)
   - Aguacate → guacamole con relleno
   - Carne premium → marbling B
3. **Reducir porción** (con cuidado de percepción):
   - 200g → 180g rara vez se nota
   - Ajustar plato/presentación
4. **Aumentar precio** si justificable:
   - Cambio de ingrediente premium
   - Inflación
   - Mejora en presentación
5. **Eliminar plato** si nada de arriba funciona

## Diseño del menú físico

### Reglas de oro
- **Lo más rentable arriba o esquinas** (zonas de mayor atención)
- **Evitar el signo $** en la carta (estudio de Cornell, Yang/Kimes/Sessarego 2009: mayor gasto sin el signo); el precio total con IVA debe seguir siendo visible (LFPC)
- **Descripciones evocativas** ("pollo asado al carbón" > "pollo asado")
- **No más de 7 platos por categoría** (sobrecarga)
- **Cuadros / sombras** para destacar 1-2 platos por categoría

### Trampas comunes
- ❌ Menú con 80 platos (cocina no puede ser excelente en todo)
- ❌ Fotos de baja calidad o de solo algunos platos sin criterio (destaca con foto los que quieres vender)
- ❌ Precios alineados verticalmente (cliente compara precio en vez de plato)

## Output estructurado

```json
{
  "analisis_menu": {
    "fecha_corte": "2026-03-31",
    "total_platos_activos": 32,
    "ventas_periodo_mxn": 480000,
    "food_cost_promedio_porcentaje": 0.34,
    "matriz_bcg": {
      "estrellas": [
        {"plato": "Mole poblano", "vendidos": 320, "contribucion_mxn": 62400}
      ],
      "vacas_lecheras": [
        {"plato": "Tacos al pastor", "accion_sugerida": "Subir precio $10 o reducir costo de porción"}
      ],
      "dilemas": [
        {"plato": "Aguachile", "fc": 0.47, "accion_sugerida": "Reposicionar + bajar costo de ingredientes"}
      ],
      "perros": [
        {"plato": "Pozole", "accion_sugerida": "Rediseñar o retirar"},
        {"plato": "Ensalada César", "accion_sugerida": "Rediseñar o retirar"}
      ]
    },
    "umbral_popularidad_unidades": 210.7,
    "margen_promedio_ponderado_mxn": 132.60,
    "platos_a_subir_precio": ["Tacos al pastor: +$10"],
    "impacto_maximo_mensual_mxn": 8500,
    "nota_impacto": "850 u × $10, suponiendo que la demanda no cae; es cota superior",
    "recomendaciones_diseño_menu": [
      "Mole poblano en la zona de mayor atención de la carta",
      "Foto y descripción para Aguachile",
      "Revisar receta de Pozole y Ensalada César"
    ]
  }
}
```

## Validación pendiente

- Benchmarks de food cost por tipo de restaurante (mexicano vs italiano vs sushi)
- Casos de éxito de reformulación específica
- Software de gestión de menú (Toast, Square, Loyverse) integraciones
