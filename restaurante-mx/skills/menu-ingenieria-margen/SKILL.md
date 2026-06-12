---
name: menu-ingenieria-margen
description: Ingeniería de menú para restaurantes mexicanos usando matriz BCG (estrellas, vacas, perros, dilemas) basada en popularidad (ventas) y margen (precio - food cost). Identifica platos a promover, reposicionar, rediseñar o eliminar. Calcula food cost ideal (28-32%), precio sugerido para alcanzar margen objetivo, alternativas para reducir costo de ingredientes. Usar cuando el usuario diga ingeniería menú, qué platos quitar, plato más rentable, food cost, margen restaurante, optimizar menú. NO usar para inventario (otro skill) ni delivery aggregators.
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

Objetivo MX típico:
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

Umbral de "popular": ≥ 70% del promedio.

## Ejemplo: 5 platos de un menú

| Plato | Precio | Food Cost | FC % | Vendidos/mes | Margen/u | Total mes |
|---|---|---|---|---|---|---|
| Mole poblano | $280 | $85 | 30% | 320 | $195 | $62,400 |
| Tacos al pastor | $145 | $35 | 24% | 850 | $110 | $93,500 |
| Pozole | $195 | $75 | 38% | 90 | $120 | $10,800 |
| Aguachile | $310 | $145 | 47% | 65 | $165 | $10,725 |
| Ensalada César | $165 | $42 | 25% | 180 | $123 | $22,140 |

### Análisis BCG

- **Tacos al pastor**: ⭐ ESTRELLA (alto volumen + buen margen)
- **Mole poblano**: 🐄 VACA (alto volumen + margen estándar) → subir precio $20-30 sin perder demanda
- **Ensalada César**: ❓ DILEMA (margen excelente pero bajo volumen) → mejorar fotos, sugerir como acompañamiento
- **Pozole**: 🐶 PERRO (food cost alto + bajo volumen) → o redesigna o elimina
- **Aguachile**: 🐶 PERRO crítico (FC 47% es muy malo) → ELIMINAR o cambiar ingredientes

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
- **NO usar $** ni precios obvios (estudios muestran menos pedido)
- **Descripciones evocativas** ("pollo asado al carbón" > "pollo asado")
- **No más de 7 platos por categoría** (sobrecarga)
- **Cuadros / sombras** para destacar 1-2 platos por categoría

### Trampas comunes
- ❌ Menú con 80 platos (cocina no puede ser excelente en todo)
- ❌ Foto solo de algunos platos (los sin foto venden 25% menos)
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
        {"plato": "Tacos al pastor", "vendidos": 850, "contribucion_mxn": 93500}
      ],
      "vacas_lecheras": [
        {"plato": "Mole poblano", "accion_sugerida": "Subir precio $25"}
      ],
      "dilemas": [
        {"plato": "Ensalada César", "accion_sugerida": "Foto + descripción + sugerir como acompañamiento"}
      ],
      "perros": [
        {"plato": "Aguachile", "fc": 0.47, "accion_sugerida": "ELIMINAR o reformular"}
      ]
    },
    "platos_a_eliminar": ["Aguachile"],
    "platos_a_subir_precio": ["Mole poblano: +$25", "Pozole: +$15"],
    "impacto_estimado_mensual_mxn": 18500,
    "recomendaciones_diseño_menu": [
      "Mover Tacos al pastor a esquina superior derecha",
      "Foto profesional de Ensalada César",
      "Quitar Aguachile del menú próximo update"
    ]
  }
}
```

## Validación pendiente

- Benchmarks de food cost por tipo de restaurante (mexicano vs italiano vs sushi)
- Casos de éxito de reformulación específica
- Software de gestión de menú (Toast, Square, Loyverse) integraciones
