---
name: comparables-zona
description: Análisis de comparables de zona para fijar precio de venta o renta de un inmueble. Consulta inmuebles24 + vivanuncios para estadísticas (p25, mediana, p75) por tipo + metros + zona + antigüedad. Identifica precio óptimo según objetivo (venta rápida vs maximizar precio). Genera reporte de mercado. Usar cuando el usuario diga comparables, precio zona, mercado renta, precio venta, m2 zona, mediana precio. NO usar para contrato (otro skill) ni screening (otro skill).
allowed-tools: Read, Write, Edit
---

# Comparables de zona

## Inputs

Para un inmueble dado:
- Tipo (casa, departamento, terreno, etc.)
- Metros cuadrados (terreno + construidos)
- Habitaciones + baños
- Ubicación (colonia + ciudad + estado)
- Antigüedad
- Amenidades (alberca, gym, seguridad)
- Tipo operación (venta vs renta)

## Fuentes de datos

### Inmuebles24 (`mp_inmuebles24`)
- Cobertura: nacional MX
- Audiencia: profesional/premium
- Datos: precio listado (no necesariamente cerrado)

### Vivanuncios (`mp_vivanuncios`)
- Cobertura: nacional MX
- Audiencia: masiva
- Datos: precio listado

### Idealista MX / Lamudi (si disponibles)
- Premium internacional

### Datos cerrados (transacciones reales)
- Notarios (acceso limitado)
- RPP (Registro Público de Propiedad)
- Avalúos bancarios (más confiables)

## Cálculos clave

### Por m²
```
precio_por_m2 = precio_listing / metros_construidos
```

### Estadísticas por zona
- P25 (percentil 25): precio bajo
- Mediana
- P75: precio alto
- Promedio
- Rango (min, max)

### Adjustment factors
Comparables exactos son raros. Ajustar:

| Factor | Diferencia | Ajuste |
|---|---|---|
| Más metros | +10% | +5-7% precio |
| Más metros terreno (casa) | +20% | +10% precio |
| Más baños | +1 baño | +3-5% precio |
| Estacionamiento | +1 lugar | +5-8% precio |
| Antigüedad mayor | +10 años | -3-5% precio |
| Sin amenidades vs con (alberca/gym) | menos amenidades | -5-10% precio |
| Piso alto (departamento) | +10 pisos | +2-3% precio |
| Vista premium | con vista | +3-7% precio |
| Sin estacionamiento | sin | -10-15% precio |

## Identificar precio óptimo

### Objetivo: venta rápida (< 30 días)
- Listar 5-10% bajo mediana del mercado
- Foto de calidad pro
- Tour 3D opcional
- Difusión amplia

### Objetivo: maximizar precio
- Listar 5-10% sobre mediana
- Tiempo en mercado: 60-180 días
- Mejor presentación
- Negociar el cierre

### Objetivo: precio justo de mercado
- Mediana de comparables
- Tiempo: 30-60 días típico

## Cómo identificar mal precio

### Sobrevalorado
- Listado > 30 días sin contactos
- < 5 vistas por semana
- Solicitudes con mucha negociación
- Reducir 5-10%

### Subvalorado
- Múltiples ofertas en primera semana
- Cierre rápido con precio listado
- Indica que se pudo cobrar más

## Output estructurado

```json
{
  "analisis_comparables": {
    "inmueble_evaluado": {
      "tipo": "departamento",
      "metros": 95,
      "habitaciones": 3,
      "ubicacion": "Polanco, CDMX",
      "antigüedad_años": 8
    },
    "muestra_comparables": {
      "total_encontrados": 47,
      "filtrados_relevantes": 22,
      "fuentes": ["inmuebles24", "vivanuncios"]
    },
    "estadisticas_venta_mxn": {
      "p25": 4_500_000,
      "mediana": 5_400_000,
      "p75": 6_300_000,
      "promedio": 5_450_000,
      "min": 3_900_000,
      "max": 7_100_000
    },
    "precio_por_m2_mxn": {
      "p25": 47_000,
      "mediana": 56_000,
      "p75": 66_000,
      "promedio": 57_000
    },
    "ajustes_aplicables": [
      {"factor": "antigüedad menor que mediana (8 vs 12 años)", "ajuste": "+3%"},
      {"factor": "1 estacionamiento (mediana tiene 1.5)", "ajuste": "-2%"}
    ],
    "precio_sugerido_mxn": {
      "venta_rapida": 5_100_000,
      "precio_justo_mercado": 5_400_000,
      "maximizar_precio": 5_700_000
    },
    "tiempo_promedio_mercado_dias": 47,
    "recomendacion": "Listar en $5,400,000 — precio justo de mercado",
    "alertas": [
      "Solo 22 comparables relevantes — mercado relativamente líquido",
      "Tiempo promedio en mercado 47 días — esperar respuesta a 30-60 días"
    ]
  }
}
```

## Validación pendiente

- Acceso a datos cerrados (no solo listings)
- Comparativa con Banxico (índice de precios vivienda)
- Software profesional (Predictum, Habi, etc.)
- Mejores prácticas en zonas premium vs medianas

## Ver también

- `mp_inmuebles24` para búsqueda de comparables
- `mp_vivanuncios` para múltiples categorías
- `ficha-inmueble` para descripción del inmueble propio
