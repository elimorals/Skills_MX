---
name: inventario-merma
description: Control de inventario para restaurantes con tracking de costo unitario, stock disponible, punto de reorden, merma esperada por ingrediente (5-12% típico restaurante, café 3-5%, frutas/verduras 8-15%), reposición automática y alertas. Detecta mermas anómalas que indican robo o desperdicio. Usar cuando el usuario diga inventario restaurante, merma, costo ingredientes, reposición, alertar bajo stock, robo cocina. NO usar para ingeniería de menú (otro skill) ni propinas.
allowed-tools: Read, Write, Edit
---

# Inventario y merma — restaurantes

## Estructura del inventario

```json
{
  "ingrediente": "Aguacate Hass",
  "categoria": "frutas_verduras",
  "stock_actual": 12.5,
  "unidad": "kg",
  "costo_unitario_mxn": 95.00,
  "valor_inventario_mxn": 1187.50,
  "punto_reorden_kg": 8.0,
  "lote_compra_estandar_kg": 25.0,
  "merma_esperada_porcentaje": 0.12,
  "vida_util_dias": 5,
  "proveedor_principal": "Central de Abastos Demo",
  "ultima_compra_fecha": "2026-03-12",
  "ultima_compra_costo_unitario": 95.00,
  "uso_promedio_diario_kg": 3.5,
  "dias_disponibles": 3.6
}
```

## Categorías típicas restaurante

| Categoría | Merma esperada | Vida útil |
|---|---|---|
| Frutas/verduras | 8-15% | 3-7 días |
| Carnes refrigeradas | 3-8% | 5-10 días |
| Carnes congeladas | 1-3% | 30-90 días |
| Pescado fresco | 10-20% | 1-3 días |
| Pescado congelado | 2-5% | 30-90 días |
| Lácteos | 2-5% | 7-21 días |
| Quesos especiales | 5-10% | 30-90 días |
| Granos secos (arroz, fríjol) | 1-3% | 12 meses |
| Aceites | 2-5% | 6-12 meses |
| Especies / condimentos | 1-2% | 12-24 meses |
| Vinos / licores | 1-3% | indefinida |

## Tipos de merma

### 1. Merma natural (esperada)
- Pérdida por evaporación, refrigeración
- Limpieza de carnes (huesos, grasa)
- Descomposición normal
- Acceptable: rango del benchmark por categoría

### 2. Merma operativa (controlable)
- Mal corte de chef
- Sobrecocción
- Pedido equivocado
- Mala recepción de mercancía

### 3. Merma anómala (sospechosa)
- Diferencia > 1.5x benchmark esperado
- Patrón sostenido > 3 días
- Coincide con turno específico

**Si detectas merma anómala**: revisar el turno, contar inventario sorpresa, instalar cámara, hablar con el chef.

## Punto de reorden + lote

```
punto_reorden = (uso_promedio_diario × días_lead_time) + safety_stock
lote_compra = uso_mensual_promedio × 1.2  # buffer 20%
```

Ejemplo aguacate:
- Uso promedio: 3.5 kg/día
- Lead time proveedor: 1 día
- Safety stock: 2 días
- Punto reorden: (3.5 × 1) + (3.5 × 2) = 10.5 kg

Cuando stock baja a 10.5 kg, sistema **alerta para reorden**.

## Recepción de mercancía

Al recibir orden:
1. Verificar cantidad vs orden de compra
2. Verificar calidad (frescura, color, temperatura)
3. Pesar/contar realmente (no confiar en albarán)
4. Fotografía si hay rechazo (evidencia para proveedor)
5. Etiquetar con fecha de recepción + vida útil
6. Capturar en sistema con costo y cantidad real

## Cierre de inventario semanal/mensual

```
inventario_inicial + compras - inventario_final = consumo_real
consumo_teorico = sum(platos_vendidos × receta_estandar)
diferencia = consumo_real - consumo_teorico
merma_observada = diferencia / consumo_real
```

Si `merma_observada > benchmark × 1.3`: **investigar**.

## Alertas automáticas

| Alerta | Trigger |
|---|---|
| Stock bajo | stock < punto_reorden |
| Por vencer | dias_para_vencer ≤ 3 |
| Merma anómala | merma_semanal > benchmark × 1.5 |
| Precio compra subió | costo_actual > costo_prev × 1.10 |
| Faltante en recepción | recibido < ordenado |

## Output estructurado

```json
{
  "estado_inventario": {
    "fecha": "2026-03-15",
    "total_ingredientes_tracked": 87,
    "valor_inventario_total_mxn": 245000,
    "ingredientes_bajo_stock": [
      {
        "ingrediente": "Aguacate Hass",
        "stock_actual_kg": 4.5,
        "punto_reorden_kg": 10.5,
        "dias_disponibles": 1.3,
        "urgencia": "ALTA"
      }
    ],
    "ingredientes_por_vencer": [
      {
        "ingrediente": "Mariscos del día",
        "stock_kg": 3.0,
        "vence_dias": 1,
        "accion": "promover hoy en menu del día"
      }
    ],
    "merma_semanal_porcentaje": 0.08,
    "merma_esperada_porcentaje": 0.07,
    "merma_anomala_alerta": false,
    "incremento_compras_destacable": [
      {
        "ingrediente": "Pollo orgánico",
        "incremento_porcentaje": 0.15,
        "razon_sospechada": "Aumento general mercado",
        "accion_sugerida": "Renegociar proveedor o subir precio plato"
      }
    ],
    "ordenes_compra_sugeridas": [
      {
        "ingrediente": "Aguacate Hass",
        "cantidad_kg": 25,
        "costo_estimado_mxn": 2375
      }
    ]
  }
}
```

## Validación pendiente

- Benchmarks de merma actualizados 2026 por tipo restaurante
- Casos típicos de merma anómala (robos, desperdicio)
- Integración con software POS para data real
