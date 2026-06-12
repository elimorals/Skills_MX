---
name: servicios-tarifario
description: Tarifario completo de servicios para salones de belleza mexicanos con variantes (cabello corto/largo, hombre/mujer/niño), add-ons (tratamiento, peinado, brillo), tiempos reales por servicio, costos directos de producto y márgenes target. Compara contra benchmark del sector. Usar cuando el usuario diga tarifario, precios salón, cuánto cobrar, listado servicios, add-ons, escalonado por cabello. NO usar para agenda (otro skill agenda-citas-salon) ni comisiones (otro skill).
allowed-tools: Read, Write, Edit
---

# Tarifario de servicios — salones MX

Estructura el catálogo completo con variantes, add-ons y tiempos reales.

## Categorías estándar

### Corte
- Mujer (corto, mediano, largo, especial)
- Hombre (clásico, moderno, fade, decoloración)
- Niño / Niña (corte sencillo)

### Color
- Tinte sencillo (raíz)
- Tinte completo
- Mechas (parciales / completas)
- Decoloración + tono fantasía
- Balayage / Highlights

### Tratamientos
- Hidratación profunda
- Keratina (alisado)
- Botox capilar
- Reparación química

### Peinados
- Recogido / chongo
- Ondas / rizos
- Brushing express
- Peinado novia

### Spa / Estética
- Facial (limpieza, hidratación, anti-edad)
- Manicure / pedicure (con o sin gel)
- Depilación (cera, láser)
- Masaje (sueco, relajante, descontracturante)

### Barbería
- Corte hombre
- Barba (forma, perfilado)
- Combo corte + barba
- Tinte de barba

## Estructura de un servicio

```json
{
  "servicio": "Tinte completo + lavado + corte",
  "categoria": "color",
  "variantes": {
    "cabello_corto": {"duracion_min": 90, "precio_mxn": 850},
    "cabello_mediano": {"duracion_min": 120, "precio_mxn": 1100},
    "cabello_largo": {"duracion_min": 150, "precio_mxn": 1450},
    "cabello_extra_largo": {"duracion_min": 180, "precio_mxn": 1800}
  },
  "add_ons_compatibles": [
    {"nombre": "tratamiento_hidratacion", "precio_mxn": 250, "duracion_extra_min": 20},
    {"nombre": "peinado_premium", "precio_mxn": 200, "duracion_extra_min": 25}
  ],
  "costo_producto_estimado_mxn": 180,
  "margen_estimado": 0.79,
  "estilista_requerido_nivel": "intermedio | senior"
}
```

## Benchmark de precios (referencia 2026)

⚠ Variabilidad enorme — son rangos típicos en CDMX, GDL, MTY. Salones de barrio cobran 30-50% menos, premium 50-100% más.

| Servicio | Barrio | Estándar | Premium |
|---|---|---|---|
| Corte mujer mediano | $250 | $450 | $850+ |
| Corte hombre | $120 | $200 | $400+ |
| Tinte completo largo | $850 | $1,450 | $2,800+ |
| Mechas completas | $1,200 | $2,200 | $4,500+ |
| Keratina | $1,500 | $2,800 | $5,500+ |
| Facial estándar | $400 | $750 | $1,500+ |
| Manicure gel | $200 | $350 | $600+ |
| Masaje 60 min | $450 | $850 | $1,800+ |

## Reglas de tarificación

### 1. Escalado por cabello largo
- Corto (hasta hombros): base
- Mediano: +20%
- Largo: +40%
- Extra largo (cintura+): +60%

### 2. Color sobre cabello previamente teñido
Cobrar tinte completo (no raíz), incluso si visualmente parece raíz.

### 3. Servicios premium (madrugada / domingo / festivos)
- Domingo: +25%
- Día festivo: +30%
- Servicio express (< 30 min de espera): +20%

### 4. Servicios primera vez
- Descuento 15-20% para nuevo cliente
- Vence en 30 días
- 1 vez por cliente

## Costos directos del producto

Para márgen real:

| Servicio | Costo producto típico (MXN) |
|---|---|
| Corte | $20-40 (pinzas, talco, gel) |
| Tinte sencillo | $80-150 (tinte, agua oxigenada) |
| Tinte completo | $150-300 |
| Mechas | $300-600 |
| Tratamiento | $50-150 |
| Facial | $80-200 |
| Manicure gel | $40-80 (esmalte gel) |

## Output estructurado

```json
{
  "tarifario": {
    "actualizacion": "2026-03-15",
    "total_servicios": 28,
    "servicios_por_categoria": {
      "corte": 6,
      "color": 5,
      "tratamientos": 4,
      "peinados": 3,
      "estetica": 7,
      "barberia": 3
    },
    "rangos_precio_mxn": {"min": 120, "max": 5500, "mediana": 750},
    "margen_promedio": 0.74,
    "alertas": [
      "Servicio 'Mechas' margen 0.55 — revisar costo producto vs precio",
      "Falta variante 'cabello largo' para 'Keratina'"
    ]
  }
}
```

## Validación pendiente

- Tarifas vigentes 2026 por zona/ciudad
- Costos producto reales con proveedores actuales
- Comparativo con Yelp/Google Maps de competidores cercanos
- Tasas premium por temporada (Navidad, San Valentín, 15 años)
